#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mscatter.c */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matscattergetvecscatter_ MATSCATTERGETVECSCATTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matscattergetvecscatter_ matscattergetvecscatter
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatescatter_ MATCREATESCATTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatescatter_ matcreatescatter
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matscattersetvecscatter_ MATSCATTERSETVECSCATTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matscattersetvecscatter_ matscattersetvecscatter
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matscattergetvecscatter_(Mat mat,VecScatter *scatter, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatScatterGetVecScatter(
	(Mat)PetscToPointer((mat) ),scatter);
}
PETSC_EXTERN void  matcreatescatter_(MPI_Fint * comm,VecScatter *scatter,Mat *A, int *ierr)
{
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateScatter(
	MPI_Comm_f2c(*(comm)),*scatter,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  matscattersetvecscatter_(Mat mat,VecScatter *scatter, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatScatterSetVecScatter(
	(Mat)PetscToPointer((mat) ),*scatter);
}
#if defined(__cplusplus)
}
#endif
