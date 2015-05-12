#include <assert.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>


#define N 10
int A[N][N], B[N][N];
int C[N][N], C1[N][N];
int main(void) {
  int i, j, k;
  double Start, End;
  omp_set_dynamic(0);
  omp_set_num_threads(2);

  srand((int)time(NULL));
  for (i = 0; i < N; ++i) {
    for (j = 0; j < N; ++j) {
      A[i][j] = rand() % 100;
      B[i][j] = rand() % 100;
    }
  }
  // printf("---- Serial\n");
  Start = omp_get_wtime();
  for (i = 0; i < N; ++i) {
    for (j = 0; j < N; ++j) {
      int Sum = 0;
      for (k = 0; k < N; ++k) {
        Sum += A[i][k] * B[k][j];
      }
      C[i][j] = Sum;
    }
  }
  End = omp_get_wtime();
  //printf("---- Serial done in %f seconds.\n", End - Start);
  //printf("---- Parallel\n");
  Start = omp_get_wtime();

int c;
for (i = 0; i < N; ++i) {
    for (j = 0; j < N; ++j) {
      C1[i][j] = 0;
    }
  }

// put the k loop on the outside
#pragma omp parallel for private(c)
  for (k = 0; k < N; ++k) {
    for (j = 0; j < N; ++j) {
      for (i = 0; i < N; ++i) {
        c = C1[i][j];
        c += B[k][j] * A[i][k];
        C1[i][j] =  c;
      }
    }
  }

  End = omp_get_wtime();
  // printf("---- Parallel done in %f seconds.\n", End - Start);
  // printf("---- Check\n");
  for (i = 0; i < N; i++) {
    for (j = 0; j < N; j++) {
      assert (C[i][j] == C1[i][j]);
    }
  }
  // printf("Passed\n");
  return 0;
}
