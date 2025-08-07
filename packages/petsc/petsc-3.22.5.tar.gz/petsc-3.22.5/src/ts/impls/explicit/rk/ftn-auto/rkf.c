#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* rk.c */
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
#define tsrkgetorder_ TSRKGETORDER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsrkgetorder_ tsrkgetorder
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsrksettype_ TSRKSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsrksettype_ tsrksettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsrkgettype_ TSRKGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsrkgettype_ tsrkgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsrksetmultirate_ TSRKSETMULTIRATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsrksetmultirate_ tsrksetmultirate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsrkgetmultirate_ TSRKGETMULTIRATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsrkgetmultirate_ tsrkgetmultirate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tsrkgetorder_(TS ts,PetscInt *order, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLINTEGER(order);
*ierr = TSRKGetOrder(
	(TS)PetscToPointer((ts) ),order);
}
PETSC_EXTERN void  tsrksettype_(TS ts,char *rktype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
/* insert Fortran-to-C conversion for rktype */
  FIXCHAR(rktype,cl0,_cltmp0);
*ierr = TSRKSetType(
	(TS)PetscToPointer((ts) ),_cltmp0);
  FREECHAR(rktype,_cltmp0);
}
PETSC_EXTERN void  tsrkgettype_(TS ts,char *rktype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
*ierr = TSRKGetType(
	(TS)PetscToPointer((ts) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for rktype */
*ierr = PetscStrncpy(rktype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, rktype, cl0);
}
PETSC_EXTERN void  tsrksetmultirate_(TS ts,PetscBool *use_multirate, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSRKSetMultirate(
	(TS)PetscToPointer((ts) ),*use_multirate);
}
PETSC_EXTERN void  tsrkgetmultirate_(TS ts,PetscBool *use_multirate, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSRKGetMultirate(
	(TS)PetscToPointer((ts) ),use_multirate);
}
#if defined(__cplusplus)
}
#endif
