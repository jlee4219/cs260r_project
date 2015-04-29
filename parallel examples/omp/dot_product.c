# include <stdlib.h>
# include <stdio.h>
# include <math.h>
# include <omp.h>
#include <assert.h>

int main ( int argc, char *argv[] );
int test01 ( int n, int x[], int y[] );
int test02 ( int n, int x[], int y[] );

/******************************************************************************/

int main ( int argc, char *argv[] )
{
  int i;
  int n;
  double wtime;
  int *x;
  int xdoty;
  int *y;

  printf ( "\n" );
  printf ( "DOT_PRODUCT\n" );
  printf ( "  C/OpenMP version\n" );
  printf ( "\n" );
  printf ( "  A program which computes a vector dot product.\n" );

  printf ( "\n" );
  printf ( "  Number of processors available = %d\n", omp_get_num_procs ( ) );
  printf ( "  Number of threads =              %d\n", omp_get_max_threads ( ) );
/*
  Set up the vector data.
  N may be increased to get better timing data.

  The value FACTOR is chosen so that the correct value of the dot product
  of X and Y is N.
*/
  n = 10000;

  while ( n < 100000000 )
  {
    n = n * 10;

    x = ( int * ) malloc ( n * sizeof ( int ) );
    y = ( int * ) malloc ( n * sizeof ( int ) );

    for ( i = 0; i < n; i++ )
    {
      x[i] = ( i + 1 ) % 7;
    }

    for ( i = 0; i < n; i++ )
    {
      y[i] = ( i + 1 ) % 7;
    }

    printf ( "\n" );
/*
  Test #1
*/
    wtime = omp_get_wtime ( );

    int xdoty1 = test01 ( n, x, y );

    wtime = omp_get_wtime ( ) - wtime;

    printf ( "  Sequential  %8d  %8d  %15.10f\n", n, xdoty1, wtime );
/*
  Test #2
*/
    wtime = omp_get_wtime ( );

    int xdoty2 = test02 ( n, x, y );

    wtime = omp_get_wtime ( ) - wtime;

    printf ( "  Parallel    %8d  %8d  %15.10f\n", n, xdoty2, wtime );

    assert(xdoty1==xdoty2);

    free ( x );
    free ( y );
  }
/*
  Terminate.
*/
  printf ( "\n" );
  printf ( "DOT_PRODUCT\n" );
  printf ( "  Normal end of execution.\n" );

  return 0;
}
/******************************************************************************/

int test01 ( int n, int x[], int y[] )

/******************************************************************************/
{
  int i;
  int xdoty;

  xdoty = 0;

  for ( i = 0; i < n; i++ )
  {
    xdoty = xdoty + x[i] * y[i];
  }

  return xdoty;
}
/******************************************************************************/

int test02 ( int n, int x[], int y[] )

/******************************************************************************/
{
  int i;
  int t;
  int xdoty;

  xdoty = 0;

# pragma omp parallel \
  shared ( n, x, y, xdoty ) \
  private ( i,t )

# pragma omp for
  for ( i = 0; i < n; i++ )
  {
    // atomicity violation
    xdoty += x[i]*y[i];
  }

  return xdoty;
}
