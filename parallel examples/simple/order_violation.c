#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <assert.h>


int* sand_castle = NULL;


void* make_sand_castle (void* arg) {

  // bide our time
  int j;
  j = 1;

  // then return our reciprocal
  sand_castle = &j;


}


void* plus_one (void* arg){

  int temp = *sand_castle;
  temp += 1;
  sand_castle = &temp;

}

int main () {

  pthread_t threads[2];

  int i = 0;
  pthread_create(threads+i, NULL, &make_sand_castle, NULL);

  i += 1;
  usleep(10);
  pthread_create(threads+i, NULL, &plus_one, NULL);

  for(i = 0; i < 2; ++i){
    pthread_join(threads[i], NULL);
  }

  return 0;
}
