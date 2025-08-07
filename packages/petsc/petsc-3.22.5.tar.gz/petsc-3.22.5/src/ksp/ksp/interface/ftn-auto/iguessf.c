#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* iguess.c */
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
#define kspguesssetfromoptions_ KSPGUESSSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspguesssetfromoptions_ kspguesssetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspguesssettolerance_ KSPGUESSSETTOLERANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspguesssettolerance_ kspguesssettolerance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspguessdestroy_ KSPGUESSDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspguessdestroy_ kspguessdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspguessview_ KSPGUESSVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspguessview_ kspguessview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspguesscreate_ KSPGUESSCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspguesscreate_ kspguesscreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspguesssettype_ KSPGUESSSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspguesssettype_ kspguesssettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspguessgettype_ KSPGUESSGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspguessgettype_ kspguessgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspguessupdate_ KSPGUESSUPDATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspguessupdate_ kspguessupdate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspguessformguess_ KSPGUESSFORMGUESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspguessformguess_ kspguessformguess
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspguesssetup_ KSPGUESSSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspguesssetup_ kspguesssetup
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  kspguesssetfromoptions_(KSPGuess guess, int *ierr)
{
CHKFORTRANNULLOBJECT(guess);
*ierr = KSPGuessSetFromOptions(
	(KSPGuess)PetscToPointer((guess) ));
}
PETSC_EXTERN void  kspguesssettolerance_(KSPGuess guess,PetscReal *tol, int *ierr)
{
CHKFORTRANNULLOBJECT(guess);
*ierr = KSPGuessSetTolerance(
	(KSPGuess)PetscToPointer((guess) ),*tol);
}
PETSC_EXTERN void  kspguessdestroy_(KSPGuess *guess, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(guess);
 PetscBool guess_null = !*(void**) guess ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(guess);
*ierr = KSPGuessDestroy(guess);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! guess_null && !*(void**) guess) * (void **) guess = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(guess);
 }
PETSC_EXTERN void  kspguessview_(KSPGuess guess,PetscViewer view, int *ierr)
{
CHKFORTRANNULLOBJECT(guess);
CHKFORTRANNULLOBJECT(view);
*ierr = KSPGuessView(
	(KSPGuess)PetscToPointer((guess) ),PetscPatchDefaultViewers((PetscViewer*)view));
}
PETSC_EXTERN void  kspguesscreate_(MPI_Fint * comm,KSPGuess *guess, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(guess);
 PetscBool guess_null = !*(void**) guess ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(guess);
*ierr = KSPGuessCreate(
	MPI_Comm_f2c(*(comm)),guess);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! guess_null && !*(void**) guess) * (void **) guess = (void *)-2;
}
PETSC_EXTERN void  kspguesssettype_(KSPGuess guess,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(guess);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = KSPGuessSetType(
	(KSPGuess)PetscToPointer((guess) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  kspguessgettype_(KSPGuess guess,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(guess);
*ierr = KSPGuessGetType(
	(KSPGuess)PetscToPointer((guess) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  kspguessupdate_(KSPGuess guess,Vec rhs,Vec sol, int *ierr)
{
CHKFORTRANNULLOBJECT(guess);
CHKFORTRANNULLOBJECT(rhs);
CHKFORTRANNULLOBJECT(sol);
*ierr = KSPGuessUpdate(
	(KSPGuess)PetscToPointer((guess) ),
	(Vec)PetscToPointer((rhs) ),
	(Vec)PetscToPointer((sol) ));
}
PETSC_EXTERN void  kspguessformguess_(KSPGuess guess,Vec rhs,Vec sol, int *ierr)
{
CHKFORTRANNULLOBJECT(guess);
CHKFORTRANNULLOBJECT(rhs);
CHKFORTRANNULLOBJECT(sol);
*ierr = KSPGuessFormGuess(
	(KSPGuess)PetscToPointer((guess) ),
	(Vec)PetscToPointer((rhs) ),
	(Vec)PetscToPointer((sol) ));
}
PETSC_EXTERN void  kspguesssetup_(KSPGuess guess, int *ierr)
{
CHKFORTRANNULLOBJECT(guess);
*ierr = KSPGuessSetUp(
	(KSPGuess)PetscToPointer((guess) ));
}
#if defined(__cplusplus)
}
#endif
