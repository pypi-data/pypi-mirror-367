#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mpiu.c */
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

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsequentialphasebegin_ PETSCSEQUENTIALPHASEBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsequentialphasebegin_ petscsequentialphasebegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsequentialphaseend_ PETSCSEQUENTIALPHASEEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsequentialphaseend_ petscsequentialphaseend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscglobalminmaxint_ PETSCGLOBALMINMAXINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscglobalminmaxint_ petscglobalminmaxint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscglobalminmaxreal_ PETSCGLOBALMINMAXREAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscglobalminmaxreal_ petscglobalminmaxreal
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscsequentialphasebegin_(MPI_Fint * comm,int *ng, int *ierr)
{
*ierr = PetscSequentialPhaseBegin(
	MPI_Comm_f2c(*(comm)),*ng);
}
PETSC_EXTERN void  petscsequentialphaseend_(MPI_Fint * comm,int *ng, int *ierr)
{
*ierr = PetscSequentialPhaseEnd(
	MPI_Comm_f2c(*(comm)),*ng);
}
PETSC_EXTERN void  petscglobalminmaxint_(MPI_Fint * comm, PetscInt minMaxVal[2],PetscInt minMaxValGlobal[2], int *ierr)
{
CHKFORTRANNULLINTEGER(minMaxVal);
CHKFORTRANNULLINTEGER(minMaxValGlobal);
*ierr = PetscGlobalMinMaxInt(
	MPI_Comm_f2c(*(comm)),minMaxVal,minMaxValGlobal);
}
PETSC_EXTERN void  petscglobalminmaxreal_(MPI_Fint * comm, PetscReal minMaxVal[2],PetscReal minMaxValGlobal[2], int *ierr)
{
CHKFORTRANNULLREAL(minMaxVal);
CHKFORTRANNULLREAL(minMaxValGlobal);
*ierr = PetscGlobalMinMaxReal(
	MPI_Comm_f2c(*(comm)),minMaxVal,minMaxValGlobal);
}
#if defined(__cplusplus)
}
#endif
