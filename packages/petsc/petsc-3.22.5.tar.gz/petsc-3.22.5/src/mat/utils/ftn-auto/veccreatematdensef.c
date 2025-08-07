#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* veccreatematdense.c */
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
#define matcreatedensefromvectype_ MATCREATEDENSEFROMVECTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatedensefromvectype_ matcreatedensefromvectype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcreatedensefromvectype_(MPI_Fint * comm,char *vtype,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N,PetscInt *lda,PetscScalar *data,Mat *A, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLSCALAR(data);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
/* insert Fortran-to-C conversion for vtype */
  FIXCHAR(vtype,cl0,_cltmp0);
*ierr = MatCreateDenseFromVecType(
	MPI_Comm_f2c(*(comm)),_cltmp0,*m,*n,*M,*N,*lda,data,A);
  FREECHAR(vtype,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
