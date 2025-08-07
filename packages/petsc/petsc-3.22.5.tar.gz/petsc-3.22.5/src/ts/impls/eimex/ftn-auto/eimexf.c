#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* eimex.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscts.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tseimexsetmaxrows_ TSEIMEXSETMAXROWS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tseimexsetmaxrows_ tseimexsetmaxrows
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tseimexsetrowcol_ TSEIMEXSETROWCOL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tseimexsetrowcol_ tseimexsetrowcol
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tseimexsetordadapt_ TSEIMEXSETORDADAPT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tseimexsetordadapt_ tseimexsetordadapt
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tseimexsetmaxrows_(TS ts,PetscInt *nrows, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSEIMEXSetMaxRows(
	(TS)PetscToPointer((ts) ),*nrows);
}
PETSC_EXTERN void  tseimexsetrowcol_(TS ts,PetscInt *row,PetscInt *col, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSEIMEXSetRowCol(
	(TS)PetscToPointer((ts) ),*row,*col);
}
PETSC_EXTERN void  tseimexsetordadapt_(TS ts,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSEIMEXSetOrdAdapt(
	(TS)PetscToPointer((ts) ),*flg);
}
#if defined(__cplusplus)
}
#endif
