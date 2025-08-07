#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexrefine.c */
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
#include "petscdmplextransform.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreateprocesssf_ DMPLEXCREATEPROCESSSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreateprocesssf_ dmplexcreateprocesssf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatecoarsepointis_ DMPLEXCREATECOARSEPOINTIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatecoarsepointis_ dmplexcreatecoarsepointis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetrefinementuniform_ DMPLEXSETREFINEMENTUNIFORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetrefinementuniform_ dmplexsetrefinementuniform
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetrefinementuniform_ DMPLEXGETREFINEMENTUNIFORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetrefinementuniform_ dmplexgetrefinementuniform
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetrefinementlimit_ DMPLEXSETREFINEMENTLIMIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetrefinementlimit_ dmplexsetrefinementlimit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetrefinementlimit_ DMPLEXGETREFINEMENTLIMIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetrefinementlimit_ dmplexgetrefinementlimit
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexcreateprocesssf_(DM dm,PetscSF sfPoint,IS *processRanks,PetscSF *sfProcess, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(sfPoint);
PetscBool processRanks_null = !*(void**) processRanks ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(processRanks);
PetscBool sfProcess_null = !*(void**) sfProcess ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfProcess);
*ierr = DMPlexCreateProcessSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((sfPoint) ),processRanks,sfProcess);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! processRanks_null && !*(void**) processRanks) * (void **) processRanks = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfProcess_null && !*(void**) sfProcess) * (void **) sfProcess = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatecoarsepointis_(DM dm,IS *fpointIS, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool fpointIS_null = !*(void**) fpointIS ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fpointIS);
*ierr = DMPlexCreateCoarsePointIS(
	(DM)PetscToPointer((dm) ),fpointIS);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fpointIS_null && !*(void**) fpointIS) * (void **) fpointIS = (void *)-2;
}
PETSC_EXTERN void  dmplexsetrefinementuniform_(DM dm,PetscBool *refinementUniform, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetRefinementUniform(
	(DM)PetscToPointer((dm) ),*refinementUniform);
}
PETSC_EXTERN void  dmplexgetrefinementuniform_(DM dm,PetscBool *refinementUniform, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexGetRefinementUniform(
	(DM)PetscToPointer((dm) ),refinementUniform);
}
PETSC_EXTERN void  dmplexsetrefinementlimit_(DM dm,PetscReal *refinementLimit, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetRefinementLimit(
	(DM)PetscToPointer((dm) ),*refinementLimit);
}
PETSC_EXTERN void  dmplexgetrefinementlimit_(DM dm,PetscReal *refinementLimit, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(refinementLimit);
*ierr = DMPlexGetRefinementLimit(
	(DM)PetscToPointer((dm) ),refinementLimit);
}
#if defined(__cplusplus)
}
#endif
