#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexinterpolate.c */
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

#include "petscdmplex.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexinterpolatepointsf_ DMPLEXINTERPOLATEPOINTSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexinterpolatepointsf_ dmplexinterpolatepointsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexinterpolate_ DMPLEXINTERPOLATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexinterpolate_ dmplexinterpolate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcopycoordinates_ DMPLEXCOPYCOORDINATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcopycoordinates_ dmplexcopycoordinates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexuninterpolate_ DMPLEXUNINTERPOLATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexuninterpolate_ dmplexuninterpolate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexisinterpolated_ DMPLEXISINTERPOLATED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexisinterpolated_ dmplexisinterpolated
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexisinterpolatedcollective_ DMPLEXISINTERPOLATEDCOLLECTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexisinterpolatedcollective_ dmplexisinterpolatedcollective
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexinterpolatepointsf_(DM dm,PetscSF pointSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(pointSF);
*ierr = DMPlexInterpolatePointSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((pointSF) ));
}
PETSC_EXTERN void  dmplexinterpolate_(DM dm,DM *dmInt, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool dmInt_null = !*(void**) dmInt ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmInt);
*ierr = DMPlexInterpolate(
	(DM)PetscToPointer((dm) ),dmInt);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmInt_null && !*(void**) dmInt) * (void **) dmInt = (void *)-2;
}
PETSC_EXTERN void  dmplexcopycoordinates_(DM dmA,DM dmB, int *ierr)
{
CHKFORTRANNULLOBJECT(dmA);
CHKFORTRANNULLOBJECT(dmB);
*ierr = DMPlexCopyCoordinates(
	(DM)PetscToPointer((dmA) ),
	(DM)PetscToPointer((dmB) ));
}
PETSC_EXTERN void  dmplexuninterpolate_(DM dm,DM *dmUnint, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool dmUnint_null = !*(void**) dmUnint ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmUnint);
*ierr = DMPlexUninterpolate(
	(DM)PetscToPointer((dm) ),dmUnint);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmUnint_null && !*(void**) dmUnint) * (void **) dmUnint = (void *)-2;
}
PETSC_EXTERN void  dmplexisinterpolated_(DM dm,DMPlexInterpolatedFlag *interpolated, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexIsInterpolated(
	(DM)PetscToPointer((dm) ),interpolated);
}
PETSC_EXTERN void  dmplexisinterpolatedcollective_(DM dm,DMPlexInterpolatedFlag *interpolated, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexIsInterpolatedCollective(
	(DM)PetscToPointer((dm) ),interpolated);
}
#if defined(__cplusplus)
}
#endif
