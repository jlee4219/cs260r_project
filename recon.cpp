#include <stdio.h>
#include <iostream>
#include "pin.H"
// #include <unordered_map>
#include <sstream>
#include <string>
#include <fstream>

#define LCL_R 0
#define LCL_W 1
#define RMT_R 2
#define RMT_W 3
#define TABLE_SIZE 16777216

// class for a node in context-aware communication graph
class NODE{
public:
    int context;
    int threadid;
    int time_stamp;
    NODE* next;
    NODE(int t_id, int stamp){
        context = 0;
        threadid = t_id;
        time_stamp = stamp;
        next = NULL;
    }
};

class HashEntry {
public:
    NODE last_writer;
    NODE* sharers_list;
    void update_writer(int t_id, int stamp) {
        last_writer.threadid = t_id;
        last_writer.time_stamp = stamp;
    }
    HashEntry(int t_id, int stamp): last_writer(t_id, stamp) { }
};

class HashMap {
private:
    HashEntry **table;
public:
    HashMap() {
        table = new HashEntry*[TABLE_SIZE];
        for (int i = 0; i < TABLE_SIZE; ++i)
            table[i] = NULL;
    }

    HashEntry* get(long key){
        return table[key % TABLE_SIZE];
    }

    void put(long key, HashEntry* entry){
        table[key % TABLE_SIZE] = entry;
    }

    void print(){
        for (int i = 0; i < TABLE_SIZE; ++i){
            if (table[i] != NULL)
                cout << (table[i]->last_writer).threadid << endl;
        }
    }

    ~HashMap() {
        for (int i = 0; i < TABLE_SIZE; ++i){
            if (table[i] != NULL)
                delete table[i];
        }
        delete[] table;
    }
};

// FILE * trace;
PIN_LOCK thread_lock;
ofstream trace_stream;
HashMap* metadata = new HashMap();
// unordered_map <string, NODE> metadata;


/*string IPToString(VOID * ip){
    string ins;
    stringstream strstream;
    strstream << (long) ip;
    strstream >> ins;
    return ins;
}*/

// Print a memory read record
VOID RecordMemRead(VOID * ip, VOID * addr, THREADID threadid)
{
    PIN_GetLock(&thread_lock, threadid+1);
    // fprintf(trace,"%ld R %ld, %d\n", (long)ip, (long)addr, (int)threadid);
    // fflush(trace);
    // fprintf("%s", IPToString(ip));
    
    PIN_ReleaseLock(&thread_lock);
}

// Print a memory write record
VOID RecordMemWrite(VOID * ip, VOID * addr, THREADID threadid)
{
    if (metadata->get((long) ip) != NULL){}
    else{
        PIN_GetLock(&thread_lock, threadid+1);
        HashEntry* write = new HashEntry((int) threadid, 0);
        metadata->put((long) ip, write);
        PIN_ReleaseLock(&thread_lock);
    }
}

// Set the minimum instruction pointer
/*VOID SetMinIP(VOID * ip, VOID * addr, THREADID threadid)
{
    PIN_GetLock(&lock, threadid+1);
    min_ip = ip;
    printf("%d\n", (int)min_ip);
    PIN_ReleaseLock(&lock);
    }*/

// Pin calls this function every time a new img is loaded
// It can instrument the image, but this example merely
// counts the number of static instructions in the image

VOID ImageLoad(IMG img, VOID *v)
{    
    if(!IMG_IsMainExecutable(img))
        return;
    else {
        for (SEC sec = IMG_SecHead(img); SEC_Valid(sec); sec = SEC_Next(sec))
        { 
            for (RTN rtn = SEC_RtnHead(sec); RTN_Valid(rtn); rtn = RTN_Next(rtn))
            {
                // Prepare for processing of RTN, an  RTN is not broken up into BBLs,
                // it is merely a sequence of INSs 
                RTN_Open(rtn);
                
                for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins))
                {
                    UINT32 memOperands = INS_MemoryOperandCount(ins);

                    // Iterate over each memory operand of the instruction.
                    for (UINT32 memOp = 0; memOp < memOperands; memOp++)
                    {
                        if (INS_MemoryOperandIsRead(ins, memOp))
                        {
                            INS_InsertPredicatedCall(
                                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
                                IARG_INST_PTR,
                                IARG_MEMORYOP_EA, memOp,
                                IARG_THREAD_ID,
                                IARG_END);
                        }
                        // Note that in some architectures a single memory operand can be 
                        // both read and written (for instance incl (%eax) on IA-32)
                        // In that case we instrument it once for read and once for write.
                        if (INS_MemoryOperandIsWritten(ins, memOp))
                        {
                            INS_InsertPredicatedCall(
                                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
                                IARG_INST_PTR,
                                IARG_MEMORYOP_EA, memOp,
                                IARG_THREAD_ID,
                                IARG_END);
                        }
                    }
                }

                // to preserve space, release data associated with RTN after we have processed it
                RTN_Close(rtn);
            }
        }
    }
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr << "This tool prints a log of image load and unload events" << endl;
    cerr << " along with static instruction counts for each image." << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char * argv[])
{
    PIN_InitLock(&thread_lock);
    // prepare for image instrumentation mode
    PIN_InitSymbols();

    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();

    trace_stream.open("read_write.out");
    // Register ImageLoad to be called when an image is loaded
    IMG_AddInstrumentFunction(ImageLoad, 0);

    // Start the program, never returns
    PIN_StartProgram();
    
    metadata->print();
    trace_stream.close();
    return 0;
}