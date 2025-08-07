#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* rosw.c */
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
#define tsroswsettype_ TSROSWSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsroswsettype_ tsroswsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsroswgettype_ TSROSWGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsroswgettype_ tsroswgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsroswsetrecomputejacobian_ TSROSWSETRECOMPUTEJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsroswsetrecomputejacobian_ tsroswsetrecomputejacobian
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tsroswsettype_(TS ts,char *roswtype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
/* insert Fortran-to-C conversion for roswtype */
  FIXCHAR(roswtype,cl0,_cltmp0);
*ierr = TSRosWSetType(
	(TS)PetscToPointer((ts) ),_cltmp0);
  FREECHAR(roswtype,_cltmp0);
}
PETSC_EXTERN void  tsroswgettype_(TS ts,char *rostype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
*ierr = TSRosWGetType(
	(TS)PetscToPointer((ts) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for rostype */
*ierr = PetscStrncpy(rostype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, rostype, cl0);
}
PETSC_EXTERN void  tsroswsetrecomputejacobian_(TS ts,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSRosWSetRecomputeJacobian(
	(TS)PetscToPointer((ts) ),*flg);
}
#if defined(__cplusplus)
}
#endif
