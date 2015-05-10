#include <stdio.h>
#include <stdlib.h>
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
#define CTXT_L 5
// #define TABLE_SIZE 16777216
#define TABLE_SIZE 1000
int count = 0;
static TLS_KEY tls_key;

// class for a node in context-aware communication graph
class NODE{
public:
    unsigned long ip;
    int context;
    int threadid;
    int time_stamp;
    NODE* next;
    NODE(unsigned long ins_p, int t_id, int stamp, int ctxt){
        ip = ins_p;
        context = ctxt;
        threadid = t_id;
        time_stamp = stamp;
        next = NULL;
    }
};

class HashEntry {
public:
    NODE last_writer;
    NODE* sharers_list;

  void update_writer(unsigned long ins_p, int t_id, int stamp, int ctxt) {
        last_writer.ip = ins_p;
        last_writer.threadid = t_id;
        last_writer.time_stamp = stamp;
        last_writer.context = ctxt;
        sharers_list = NULL;
        count += 1;
    }

  void add_reader(unsigned long ins_p, int t_id, int stamp, int ctxt) {
    NODE* reader = new NODE(ins_p, t_id, stamp, ctxt);
        reader->next = sharers_list;
        sharers_list = reader;
        count += 1;
    }

    bool has_read(int t_id){
        NODE* cur = sharers_list;
        while(cur != NULL){
	    if (cur->threadid == t_id)
	        return true;
            cur = cur->next;
        }
        return false;
    }

  HashEntry(unsigned long ins_p, int t_id, int stamp, int ctxt):
    last_writer(ins_p, t_id, stamp, ctxt), sharers_list(NULL) { }
};

class HashMap {
private:
    HashEntry **table;
    ofstream trace_stream;
public:
    HashMap() {
        table = new HashEntry*[TABLE_SIZE];
        for (int i = 0; i < TABLE_SIZE; ++i)
            table[i] = NULL;
        trace_stream.open("read_write.out");
    }

    HashEntry* get(unsigned long key){
        return table[key % TABLE_SIZE];
    }

    void put(unsigned long key, HashEntry* entry){
        table[key % TABLE_SIZE] = entry;
    }

    void print_table(){
        for (int i = 0; i < TABLE_SIZE; ++i){
            if (table[i] != NULL)
	        print_edges(table[i]);
        }
    }

    void print_edges(HashEntry* entry){
        print_node(&(entry->last_writer));
        NODE* cur = entry->sharers_list;
	while (cur != NULL){
	    trace_stream << " ";
	    print_node(cur);
	    cur = cur -> next;
        }
        trace_stream << endl;
    }

    void print_node(NODE* node){
      trace_stream << node->ip << " " << node->threadid << " " << node->time_stamp << " " << node->context;
    }

    void close_stream(){
      trace_stream.close();
    }

    ~HashMap() {
        for (int i = 0; i < TABLE_SIZE; ++i){
            if (table[i] != NULL)
                delete table[i];
        }
        delete[] table;
    }
};

struct ins_type {
  short type;
  ins_type* next;
  ins_type* prev;
};

class Context {
private:
    ins_type* head;
public:
    Context() {
        head = (ins_type*) malloc(sizeof(ins_type) * CTXT_L);
        for (int i = 0; i < CTXT_L; ++i){
            (head+i)->next = head + ((i + 1) % CTXT_L);
            (head+i)->prev = head + ((CTXT_L - 1) % CTXT_L);
            (head+i)->type = -1;
        }
    }

    void add(short type){
        head = head -> prev;
        head->type = type;
    }

    int to_int(){
        ins_type* cur = head;
        int accum = 0;
        for (int i = 0; i < CTXT_L; ++i){
	    accum *= 4;
            if (cur -> type != -1)
	        accum += cur -> type;
        }
        return accum;
    }
};

Context* get_tls(THREADID threadid)
{
    Context* ctxt = static_cast<Context*>(PIN_GetThreadData(tls_key, threadid));
    return ctxt;
}

// FILE * trace;
PIN_LOCK thread_lock;
HashMap* metadata = new HashMap();

// Print a memory read record
VOID RecordMemRead(VOID * ip, VOID * addr, THREADID threadid)
{
    Context* ctxt = get_tls(threadid);
    ctxt->add(LCL_R);
    HashEntry* entry = metadata->get((unsigned long) addr);
    if (entry != NULL){
      if (!entry->has_read((int) threadid) && (int)threadid != (entry->last_writer).threadid)
	{
            PIN_GetLock(&thread_lock, threadid+1);
            entry->add_reader((unsigned long) ip, threadid, count, ctxt->to_int());
            PIN_ReleaseLock(&thread_lock);
        }
    }
}

// Print a memory write record
VOID RecordMemWrite(VOID * ip, VOID * addr, THREADID threadid)
{
    Context* ctxt = get_tls(threadid);
    ctxt->add(LCL_W);
    HashEntry* entry = metadata->get((unsigned long) addr);
    if (entry != NULL){
        if ((entry -> last_writer).threadid != (int) threadid)
	{
	    PIN_GetLock(&thread_lock, threadid+1);
            metadata->print_edges(entry);
	    entry->update_writer((unsigned long) ip, (int) threadid, count, ctxt->to_int());
	    PIN_ReleaseLock(&thread_lock);
        }
    }
    else{
        PIN_GetLock(&thread_lock, threadid+1);
        HashEntry* write = new HashEntry((unsigned long) ip,(int) threadid, count, ctxt->to_int());
        metadata->put((unsigned long) addr, write);
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
		      if (INS_MemoryOperandIsRead(ins, memOp) && !INS_IsStackRead(ins))
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
		      if (INS_MemoryOperandIsWritten(ins, memOp) && !INS_IsStackWrite(ins))
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

// Note: the other context here is a pin thing.
VOID ThreadStart(THREADID threadid, CONTEXT* ct, INT32 flags, VOID* v){
    Context* ctxt = new Context;
    PIN_SetThreadData(tls_key, ctxt, threadid);
}

VOID Fini(INT32 code, VOID* v){
    metadata->print_table();
    metadata->close_stream();
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

    tls_key = PIN_CreateThreadDataKey(0);

    // Register ImageLoad to be called when an image is loaded
    IMG_AddInstrumentFunction(ImageLoad, 0);

    PIN_AddThreadStartFunction(ThreadStart, 0);

    PIN_AddFiniFunction(Fini, 0);

    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
