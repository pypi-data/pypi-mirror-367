#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fdir.c */
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

#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmkdir_ PETSCMKDIR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmkdir_ petscmkdir
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmkdtemp_ PETSCMKDTEMP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmkdtemp_ petscmkdtemp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrmtree_ PETSCRMTREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrmtree_ petscrmtree
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscmkdir_( char dir[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for dir */
  FIXCHAR(dir,cl0,_cltmp0);
*ierr = PetscMkdir(_cltmp0);
  FREECHAR(dir,_cltmp0);
}
PETSC_EXTERN void  petscmkdtemp_(char dir[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for dir */
  FIXCHAR(dir,cl0,_cltmp0);
*ierr = PetscMkdtemp(_cltmp0);
  FREECHAR(dir,_cltmp0);
}
PETSC_EXTERN void  petscrmtree_( char dir[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for dir */
  FIXCHAR(dir,cl0,_cltmp0);
*ierr = PetscRMTree(_cltmp0);
  FREECHAR(dir,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
