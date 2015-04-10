#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>



void* p = NULL;

void *get_p()
{
  if (p != NULL) {
    int x = *(int *)p;
    assert(x == 0);
    if (x) {
      exit(1);
    }
  }
  return NULL;
}

/* this function is run by the second thread */
void *malloc_p()
{
  p = malloc(sizeof(int));
  *(int*)p = 0;
  *(int*)p = 0;
  *(int*)p = 0;
  *(int*)p = 0;
  *(int*)p = 0;
  *(int*)p = 1;
  free(p);
  p = NULL;
  return NULL;
}

int main () {
  pthread_t thread_1;
  pthread_t thread_2;
  if(pthread_create(&thread_2, NULL, malloc_p, NULL)) {
    return 1;
  }
  if(pthread_create(&thread_1, NULL, get_p, NULL)) {
    return 2;
  }
  return 0;
}