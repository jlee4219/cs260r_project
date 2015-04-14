// compile with
// gcc-4.9 -fopenmp -std=c99 dot_product.c -o dot_product

#include <assert.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>


#define N 500
int A[N][N], B[N][N];
int C[N][N], C1[N][N];
int main(void) {
  int i, j, k;
  double Start, End;

  srand((int)time(NULL));
  for (i = 0; i < N; ++i) {
    for (j = 0; j < N; ++j) {
      A[i][j] = rand() % 100;
      B[i][j] = rand() % 100;
    }
  }
  printf("---- Serial\n");
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
  printf("---- Serial done in %f seconds.\n", End - Start);
  printf("---- Parallel\n");
  Start = omp_get_wtime();

int c;
for (i = 0; i < N; ++i) {
    for (j = 0; j < N; ++j) {
      C1[i][j] = 0;
    }
  }

#pragma omp parallel for private(k, c)
  for (i = 0; i < N; ++i) {
    for (j = 0; j < N; ++j) {
      for (k = 0; k < N; ++k) {
        // atomicity violation
        c = C1[i][j];
        for (int m = 0; m < B[k][j]; ++m)
        {
          c += A[i][k];
        }
        C1[i][j] =  c;
      }
    }
  }

  End = omp_get_wtime();
  printf("---- Parallel done in %f seconds.\n", End - Start);
  printf("---- Check\n");
  for (i = 0; i < N; i++) {
    for (j = 0; j < N; j++) {
      assert (C[i][j] == C1[i][j]);
    }
  }
  printf("Passed\n");
  return 0;
}