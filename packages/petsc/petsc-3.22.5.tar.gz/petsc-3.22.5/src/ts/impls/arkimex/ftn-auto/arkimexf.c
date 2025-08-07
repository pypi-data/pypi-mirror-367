#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* arkimex.c */
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

#include "petscts.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsarkimexsettype_ TSARKIMEXSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsarkimexsettype_ tsarkimexsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsarkimexgettype_ TSARKIMEXGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsarkimexgettype_ tsarkimexgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsarkimexsetfullyimplicit_ TSARKIMEXSETFULLYIMPLICIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsarkimexsetfullyimplicit_ tsarkimexsetfullyimplicit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsarkimexgetfullyimplicit_ TSARKIMEXGETFULLYIMPLICIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsarkimexgetfullyimplicit_ tsarkimexgetfullyimplicit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsdirksettype_ TSDIRKSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsdirksettype_ tsdirksettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsdirkgettype_ TSDIRKGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsdirkgettype_ tsdirkgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsarkimexsetfastslowsplit_ TSARKIMEXSETFASTSLOWSPLIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsarkimexsetfastslowsplit_ tsarkimexsetfastslowsplit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsarkimexgetfastslowsplit_ TSARKIMEXGETFASTSLOWSPLIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsarkimexgetfastslowsplit_ tsarkimexgetfastslowsplit
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tsarkimexsettype_(TS ts,char *arktype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
/* insert Fortran-to-C conversion for arktype */
  FIXCHAR(arktype,cl0,_cltmp0);
*ierr = TSARKIMEXSetType(
	(TS)PetscToPointer((ts) ),_cltmp0);
  FREECHAR(arktype,_cltmp0);
}
PETSC_EXTERN void  tsarkimexgettype_(TS ts,char *arktype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
*ierr = TSARKIMEXGetType(
	(TS)PetscToPointer((ts) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for arktype */
*ierr = PetscStrncpy(arktype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, arktype, cl0);
}
PETSC_EXTERN void  tsarkimexsetfullyimplicit_(TS ts,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSARKIMEXSetFullyImplicit(
	(TS)PetscToPointer((ts) ),*flg);
}
PETSC_EXTERN void  tsarkimexgetfullyimplicit_(TS ts,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSARKIMEXGetFullyImplicit(
	(TS)PetscToPointer((ts) ),flg);
}
PETSC_EXTERN void  tsdirksettype_(TS ts,char *dirktype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
/* insert Fortran-to-C conversion for dirktype */
  FIXCHAR(dirktype,cl0,_cltmp0);
*ierr = TSDIRKSetType(
	(TS)PetscToPointer((ts) ),_cltmp0);
  FREECHAR(dirktype,_cltmp0);
}
PETSC_EXTERN void  tsdirkgettype_(TS ts,char *dirktype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
*ierr = TSDIRKGetType(
	(TS)PetscToPointer((ts) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for dirktype */
*ierr = PetscStrncpy(dirktype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, dirktype, cl0);
}
PETSC_EXTERN void  tsarkimexsetfastslowsplit_(TS ts,PetscBool *fastslow, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSARKIMEXSetFastSlowSplit(
	(TS)PetscToPointer((ts) ),*fastslow);
}
PETSC_EXTERN void  tsarkimexgetfastslowsplit_(TS ts,PetscBool *fastslow, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSARKIMEXGetFastSlowSplit(
	(TS)PetscToPointer((ts) ),fastslow);
}
#if defined(__cplusplus)
}
#endif
