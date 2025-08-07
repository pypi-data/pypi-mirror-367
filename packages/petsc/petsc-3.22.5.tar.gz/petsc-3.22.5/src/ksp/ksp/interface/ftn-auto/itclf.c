#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* itcl.c */
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

#include "petscksp.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsetoptionsprefix_ KSPSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsetoptionsprefix_ kspsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspappendoptionsprefix_ KSPAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspappendoptionsprefix_ kspappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsetusefischerguess_ KSPSETUSEFISCHERGUESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsetusefischerguess_ kspsetusefischerguess
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsetguess_ KSPSETGUESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsetguess_ kspsetguess
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspgetguess_ KSPGETGUESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspgetguess_ kspgetguess
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspgetoptionsprefix_ KSPGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspgetoptionsprefix_ kspgetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsetfromoptions_ KSPSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsetfromoptions_ kspsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspresetfromoptions_ KSPRESETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspresetfromoptions_ kspresetfromoptions
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  kspsetoptionsprefix_(KSP ksp, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ksp);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = KSPSetOptionsPrefix(
	(KSP)PetscToPointer((ksp) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  kspappendoptionsprefix_(KSP ksp, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ksp);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = KSPAppendOptionsPrefix(
	(KSP)PetscToPointer((ksp) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  kspsetusefischerguess_(KSP ksp,PetscInt *model,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPSetUseFischerGuess(
	(KSP)PetscToPointer((ksp) ),*model,*size);
}
PETSC_EXTERN void  kspsetguess_(KSP ksp,KSPGuess guess, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
CHKFORTRANNULLOBJECT(guess);
*ierr = KSPSetGuess(
	(KSP)PetscToPointer((ksp) ),
	(KSPGuess)PetscToPointer((guess) ));
}
PETSC_EXTERN void  kspgetguess_(KSP ksp,KSPGuess *guess, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
PetscBool guess_null = !*(void**) guess ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(guess);
*ierr = KSPGetGuess(
	(KSP)PetscToPointer((ksp) ),guess);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! guess_null && !*(void**) guess) * (void **) guess = (void *)-2;
}
PETSC_EXTERN void  kspgetoptionsprefix_(KSP ksp, char *prefix, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPGetOptionsPrefix(
	(KSP)PetscToPointer((ksp) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for prefix */
*ierr = PetscStrncpy(prefix, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, prefix, cl0);
}
PETSC_EXTERN void  kspsetfromoptions_(KSP ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPSetFromOptions(
	(KSP)PetscToPointer((ksp) ));
}
PETSC_EXTERN void  kspresetfromoptions_(KSP ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPResetFromOptions(
	(KSP)PetscToPointer((ksp) ));
}
#if defined(__cplusplus)
}
#endif
