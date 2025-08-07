#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* sorder.c */
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
#define matgetordering_ MATGETORDERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetordering_ matgetordering
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matgetordering_(Mat mat,char *type,IS *rperm,IS *cperm, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
PetscBool rperm_null = !*(void**) rperm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rperm);
PetscBool cperm_null = !*(void**) cperm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cperm);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = MatGetOrdering(
	(Mat)PetscToPointer((mat) ),_cltmp0,rperm,cperm);
  FREECHAR(type,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rperm_null && !*(void**) rperm) * (void **) rperm = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cperm_null && !*(void**) cperm) * (void **) cperm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
