#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* prefix.c */
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
#define petscobjectgetoptions_ PETSCOBJECTGETOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectgetoptions_ petscobjectgetoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectsetoptions_ PETSCOBJECTSETOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsetoptions_ petscobjectsetoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectsetoptionsprefix_ PETSCOBJECTSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsetoptionsprefix_ petscobjectsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectappendoptionsprefix_ PETSCOBJECTAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectappendoptionsprefix_ petscobjectappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectgetoptionsprefix_ PETSCOBJECTGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectgetoptionsprefix_ petscobjectgetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectprependoptionsprefix_ PETSCOBJECTPREPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectprependoptionsprefix_ petscobjectprependoptionsprefix
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscobjectgetoptions_(PetscObject obj,PetscOptions *options, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
PetscBool options_null = !*(void**) options ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(options);
*ierr = PetscObjectGetOptions(
	(PetscObject)PetscToPointer((obj) ),options);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! options_null && !*(void**) options) * (void **) options = (void *)-2;
}
PETSC_EXTERN void  petscobjectsetoptions_(PetscObject obj,PetscOptions options, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
CHKFORTRANNULLOBJECT(options);
*ierr = PetscObjectSetOptions(
	(PetscObject)PetscToPointer((obj) ),
	(PetscOptions)PetscToPointer((options) ));
}
PETSC_EXTERN void  petscobjectsetoptionsprefix_(PetscObject obj, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscObjectSetOptionsPrefix(
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  petscobjectappendoptionsprefix_(PetscObject obj, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscObjectAppendOptionsPrefix(
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  petscobjectgetoptionsprefix_(PetscObject obj, char *prefix, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectGetOptionsPrefix(
	(PetscObject)PetscToPointer((obj) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for prefix */
*ierr = PetscStrncpy(prefix, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, prefix, cl0);
}
PETSC_EXTERN void  petscobjectprependoptionsprefix_(PetscObject obj, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscObjectPrependOptionsPrefix(
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
