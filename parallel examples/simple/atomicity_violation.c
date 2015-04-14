#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <assert.h>


int global_var = 1;


void* global_reciprocal (void* arg) {
  if (global_var != 0)
  {
    // bide our time
    for (int i = 0; i < 100; ++i)
    {
      int j = i * i;
    }

    // then return our reciprocal
    global_var = 1/global_var;
  }

}


void* to_zero (void* arg){

  global_var = 0;

}

int main () {

  pthread_t threads[2];

  int i = 0;
  pthread_create(threads+i, NULL, &global_reciprocal, NULL);

  i += 1;
  pthread_create(threads+i, NULL, &to_zero, NULL);

  for(i = 0; i < 2; ++i){
    pthread_join(threads[i], NULL);
  }

  return 0;
}
