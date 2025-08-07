#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* tsrhssplit.c */
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
#define tsrhssplitsetis_ TSRHSSPLITSETIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsrhssplitsetis_ tsrhssplitsetis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsrhssplitgetis_ TSRHSSPLITGETIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsrhssplitgetis_ tsrhssplitgetis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsrhssplitgetsnes_ TSRHSSPLITGETSNES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsrhssplitgetsnes_ tsrhssplitgetsnes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsrhssplitsetsnes_ TSRHSSPLITSETSNES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsrhssplitsetsnes_ tsrhssplitsetsnes
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tsrhssplitsetis_(TS ts, char splitname[],IS is, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(is);
/* insert Fortran-to-C conversion for splitname */
  FIXCHAR(splitname,cl0,_cltmp0);
*ierr = TSRHSSplitSetIS(
	(TS)PetscToPointer((ts) ),_cltmp0,
	(IS)PetscToPointer((is) ));
  FREECHAR(splitname,_cltmp0);
}
PETSC_EXTERN void  tsrhssplitgetis_(TS ts, char splitname[],IS *is, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
/* insert Fortran-to-C conversion for splitname */
  FIXCHAR(splitname,cl0,_cltmp0);
*ierr = TSRHSSplitGetIS(
	(TS)PetscToPointer((ts) ),_cltmp0,is);
  FREECHAR(splitname,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  tsrhssplitgetsnes_(TS ts,SNES *snes, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
PetscBool snes_null = !*(void**) snes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(snes);
*ierr = TSRHSSplitGetSNES(
	(TS)PetscToPointer((ts) ),snes);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! snes_null && !*(void**) snes) * (void **) snes = (void *)-2;
}
PETSC_EXTERN void  tsrhssplitsetsnes_(TS ts,SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(snes);
*ierr = TSRHSSplitSetSNES(
	(TS)PetscToPointer((ts) ),
	(SNES)PetscToPointer((snes) ));
}
#if defined(__cplusplus)
}
#endif
