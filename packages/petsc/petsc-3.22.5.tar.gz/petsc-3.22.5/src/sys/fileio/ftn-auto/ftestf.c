#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* ftest.c */
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
#define petsctestfile_ PETSCTESTFILE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsctestfile_ petsctestfile
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsctestdirectory_ PETSCTESTDIRECTORY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsctestdirectory_ petsctestdirectory
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petsctestfile_( char fname[],char *mode,PetscBool *flg, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for fname */
  FIXCHAR(fname,cl0,_cltmp0);
*ierr = PetscTestFile(_cltmp0,*mode,flg);
  FREECHAR(fname,_cltmp0);
}
PETSC_EXTERN void  petsctestdirectory_( char dirname[],char *mode,PetscBool *flg, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for dirname */
  FIXCHAR(dirname,cl0,_cltmp0);
*ierr = PetscTestDirectory(_cltmp0,*mode,flg);
  FREECHAR(dirname,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
