#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <assert.h>
#define NUM_THREADS 2
#define NUM_INC 100000

int count = 0;

void* f (void* arg) {
  int i = 0;
  for (i; i < NUM_INC; ++i){
    ++count;
  }
}

int main () {
  pthread_t threads[NUM_THREADS];
  int i = 0;
  for (i; i < NUM_THREADS; ++i){
    pthread_create(threads+i, NULL, &f, NULL);
  }
  for(i = 0; i < NUM_THREADS; ++i){
    pthread_join(threads[i], NULL);
  }
  assert(count == NUM_THREADS * NUM_INC);
  return 0;
}
