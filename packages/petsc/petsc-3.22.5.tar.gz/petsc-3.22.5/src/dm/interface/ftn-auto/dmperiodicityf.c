#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmperiodicity.c */
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

#include "petscdm.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetperiodicity_ DMSETPERIODICITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetperiodicity_ dmsetperiodicity
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlocalizecoordinate_ DMLOCALIZECOORDINATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlocalizecoordinate_ dmlocalizecoordinate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetcoordinateslocalizedlocal_ DMGETCOORDINATESLOCALIZEDLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetcoordinateslocalizedlocal_ dmgetcoordinateslocalizedlocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetcoordinateslocalized_ DMGETCOORDINATESLOCALIZED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetcoordinateslocalized_ dmgetcoordinateslocalized
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetsparselocalize_ DMGETSPARSELOCALIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetsparselocalize_ dmgetsparselocalize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetsparselocalize_ DMSETSPARSELOCALIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetsparselocalize_ dmsetsparselocalize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlocalizecoordinates_ DMLOCALIZECOORDINATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlocalizecoordinates_ dmlocalizecoordinates
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmsetperiodicity_(DM dm, PetscReal maxCell[], PetscReal Lstart[], PetscReal L[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(maxCell);
CHKFORTRANNULLREAL(Lstart);
CHKFORTRANNULLREAL(L);
*ierr = DMSetPeriodicity(
	(DM)PetscToPointer((dm) ),maxCell,Lstart,L);
}
PETSC_EXTERN void  dmlocalizecoordinate_(DM dm, PetscScalar in[],PetscBool *endpoint,PetscScalar out[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLSCALAR(in);
CHKFORTRANNULLSCALAR(out);
*ierr = DMLocalizeCoordinate(
	(DM)PetscToPointer((dm) ),in,*endpoint,out);
}
PETSC_EXTERN void  dmgetcoordinateslocalizedlocal_(DM dm,PetscBool *areLocalized, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetCoordinatesLocalizedLocal(
	(DM)PetscToPointer((dm) ),areLocalized);
}
PETSC_EXTERN void  dmgetcoordinateslocalized_(DM dm,PetscBool *areLocalized, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetCoordinatesLocalized(
	(DM)PetscToPointer((dm) ),areLocalized);
}
PETSC_EXTERN void  dmgetsparselocalize_(DM dm,PetscBool *sparse, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetSparseLocalize(
	(DM)PetscToPointer((dm) ),sparse);
}
PETSC_EXTERN void  dmsetsparselocalize_(DM dm,PetscBool *sparse, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetSparseLocalize(
	(DM)PetscToPointer((dm) ),*sparse);
}
PETSC_EXTERN void  dmlocalizecoordinates_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMLocalizeCoordinates(
	(DM)PetscToPointer((dm) ));
}
#if defined(__cplusplus)
}
#endif
