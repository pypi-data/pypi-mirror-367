#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* swarmpic_sort.c */
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

#include "petscdmda.h"
#include "petscdmplex.h"
#include "petscdmswarm.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsortgetnumberofpointspercell_ DMSWARMSORTGETNUMBEROFPOINTSPERCELL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsortgetnumberofpointspercell_ dmswarmsortgetnumberofpointspercell
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsortgetaccess_ DMSWARMSORTGETACCESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsortgetaccess_ dmswarmsortgetaccess
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsortrestoreaccess_ DMSWARMSORTRESTOREACCESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsortrestoreaccess_ dmswarmsortrestoreaccess
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsortgetisvalid_ DMSWARMSORTGETISVALID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsortgetisvalid_ dmswarmsortgetisvalid
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsortgetsizes_ DMSWARMSORTGETSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsortgetsizes_ dmswarmsortgetsizes
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmswarmsortgetnumberofpointspercell_(DM dm,PetscInt *e,PetscInt *npoints, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(npoints);
*ierr = DMSwarmSortGetNumberOfPointsPerCell(
	(DM)PetscToPointer((dm) ),*e,npoints);
}
PETSC_EXTERN void  dmswarmsortgetaccess_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmSortGetAccess(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmswarmsortrestoreaccess_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmSortRestoreAccess(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmswarmsortgetisvalid_(DM dm,PetscBool *isvalid, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmSortGetIsValid(
	(DM)PetscToPointer((dm) ),isvalid);
}
PETSC_EXTERN void  dmswarmsortgetsizes_(DM dm,PetscInt *ncells,PetscInt *npoints, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(ncells);
CHKFORTRANNULLINTEGER(npoints);
*ierr = DMSwarmSortGetSizes(
	(DM)PetscToPointer((dm) ),ncells,npoints);
}
#if defined(__cplusplus)
}
#endif
