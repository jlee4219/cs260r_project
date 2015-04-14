#include <stdio.h>
#include <iostream>
#include "pin.H"

FILE * trace;
PIN_LOCK lock;
VOID* min_ip = NULL;

// Print a memory read record
VOID RecordMemRead(VOID * ip, VOID * addr, THREADID threadid)
{
    PIN_GetLock(&lock, threadid+1);
    fprintf(trace,"%d R %d\n", (int)min_ip - (int)ip, (int)addr);
    fflush(trace);
    PIN_ReleaseLock(&lock);
}

// Print a memory write record
VOID RecordMemWrite(VOID * ip, VOID * addr, THREADID threadid)
{
    PIN_GetLock(&lock, threadid+1);
    fprintf(trace,"%d W %d\n", (int)min_ip - (int)ip, (int)addr);
    fflush(trace);
    PIN_ReleaseLock(&lock);
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
		    if (ins == RTN_InsHead(rtn))
                    {
		      min_ip = (VOID *)INS_Address(ins);
                    }
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
    PIN_InitLock(&lock);
    // prepare for image instrumentation mode
    PIN_InitSymbols();

    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();

    trace = fopen("read_write.out", "w");
    // Register ImageLoad to be called when an image is loaded
    IMG_AddInstrumentFunction(ImageLoad, 0);

    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
