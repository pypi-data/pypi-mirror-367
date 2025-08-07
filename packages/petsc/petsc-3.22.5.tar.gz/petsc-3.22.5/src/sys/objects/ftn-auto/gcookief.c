#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* gcookie.c */
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
#define petscobjectgetclassid_ PETSCOBJECTGETCLASSID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectgetclassid_ petscobjectgetclassid
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectgetclassname_ PETSCOBJECTGETCLASSNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectgetclassname_ petscobjectgetclassname
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscobjectgetclassid_(PetscObject obj,PetscClassId *classid, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectGetClassId(
	(PetscObject)PetscToPointer((obj) ),classid);
}
PETSC_EXTERN void  petscobjectgetclassname_(PetscObject obj, char *classname, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectGetClassName(
	(PetscObject)PetscToPointer((obj) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for classname */
*ierr = PetscStrncpy(classname, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, classname, cl0);
}
#if defined(__cplusplus)
}
#endif
