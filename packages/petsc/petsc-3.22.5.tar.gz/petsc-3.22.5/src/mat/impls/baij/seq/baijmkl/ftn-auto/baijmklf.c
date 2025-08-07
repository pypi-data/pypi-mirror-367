#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* baijmkl.c */
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
#define matcreateseqbaijmkl_ MATCREATESEQBAIJMKL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateseqbaijmkl_ matcreateseqbaijmkl
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcreateseqbaijmkl_(MPI_Fint * comm,PetscInt *bs,PetscInt *m,PetscInt *n,PetscInt *nz, PetscInt nnz[],Mat *A, int *ierr)
{
CHKFORTRANNULLINTEGER(nnz);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateSeqBAIJMKL(
	MPI_Comm_f2c(*(comm)),*bs,*m,*n,*nz,nnz,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
