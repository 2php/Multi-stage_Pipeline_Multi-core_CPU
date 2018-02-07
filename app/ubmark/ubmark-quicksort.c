//========================================================================
// ubmark-quicksort
//========================================================================
// This version (v1) is brought over directly from Fall 15.

#include "common.h"
#include "ubmark-quicksort.dat"
#include <iostream>

//------------------------------------------------------------------------
// quicksort-scalar
//------------------------------------------------------------------------
int find_pivot( int dest[], int l, int r){
  int pivot, i, j, temp;
  pivot = dest[l];
  i = l;
  j = r+1;
  while (1){
    i++;j--;
    while( dest[i] <= pivot && i <= r )
      i++;
    while( dest[j] > pivot )
      j--;
    if( i >= j ) break;
    temp = dest[i];
    dest[i] = dest[j];
    dest[j] = temp;
  }
  temp = dest[l];
  dest[l] = dest[j];
  dest[j] = temp;
  return j;
}

void quicksort( int dest[], int l, int r){
  int m;
  if ( l < r){
    m = find_pivot(dest, l, r);
    quicksort(dest, l, m-1);
    quicksort(dest, m+1, r);
  }
}

__attribute__ ((noinline))
void quicksort_scalar( int* dest, int* src, int size )
{
  for (int i = 0; i<size; i++){
    dest[i] = src[i];
  } 
  quicksort( dest, 0, size-1);

}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int dest[], int ref[], int size )
{
  int i;
  for ( i = 0; i < size; i++ ) {
    if ( !( dest[i] == ref[i] ) ) {
      test_fail( i, dest[i], ref[i] );
    }
  }
  test_pass();
}

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  int dest[size];

  int i;
  for ( i = 0; i < size; i++ )
    dest[i] = 0;

  test_stats_on();
  quicksort_scalar( dest, src, size );
  test_stats_off();

  verify_results( dest, ref, size );

  return 0;
}

