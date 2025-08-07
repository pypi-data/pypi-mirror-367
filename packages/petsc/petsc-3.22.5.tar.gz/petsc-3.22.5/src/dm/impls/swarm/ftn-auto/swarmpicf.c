#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* swarmpic.c */
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

#include "petscdmswarm.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsetpointsuniformcoordinates_ DMSWARMSETPOINTSUNIFORMCOORDINATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsetpointsuniformcoordinates_ dmswarmsetpointsuniformcoordinates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsetpointcoordinates_ DMSWARMSETPOINTCOORDINATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsetpointcoordinates_ dmswarmsetpointcoordinates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarminsertpointsusingcelldm_ DMSWARMINSERTPOINTSUSINGCELLDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarminsertpointsusingcelldm_ dmswarminsertpointsusingcelldm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmcreatepointpercellcount_ DMSWARMCREATEPOINTPERCELLCOUNT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmcreatepointpercellcount_ dmswarmcreatepointpercellcount
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmgetnumspecies_ DMSWARMGETNUMSPECIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmgetnumspecies_ dmswarmgetnumspecies
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsetnumspecies_ DMSWARMSETNUMSPECIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsetnumspecies_ dmswarmsetnumspecies
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmcomputelocalsizefromoptions_ DMSWARMCOMPUTELOCALSIZEFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmcomputelocalsizefromoptions_ dmswarmcomputelocalsizefromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarminitializecoordinates_ DMSWARMINITIALIZECOORDINATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarminitializecoordinates_ dmswarminitializecoordinates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarminitializevelocitiesfromoptions_ DMSWARMINITIALIZEVELOCITIESFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarminitializevelocitiesfromoptions_ dmswarminitializevelocitiesfromoptions
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmswarmsetpointsuniformcoordinates_(DM dm,PetscReal min[],PetscReal max[],PetscInt npoints[],InsertMode *mode, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(min);
CHKFORTRANNULLREAL(max);
CHKFORTRANNULLINTEGER(npoints);
*ierr = DMSwarmSetPointsUniformCoordinates(
	(DM)PetscToPointer((dm) ),min,max,npoints,*mode);
}
PETSC_EXTERN void  dmswarmsetpointcoordinates_(DM dm,PetscInt *npoints,PetscReal coor[],PetscBool *redundant,InsertMode *mode, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(coor);
*ierr = DMSwarmSetPointCoordinates(
	(DM)PetscToPointer((dm) ),*npoints,coor,*redundant,*mode);
}
PETSC_EXTERN void  dmswarminsertpointsusingcelldm_(DM dm,DMSwarmPICLayoutType *layout_type,PetscInt *fill_param, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmInsertPointsUsingCellDM(
	(DM)PetscToPointer((dm) ),*layout_type,*fill_param);
}
PETSC_EXTERN void  dmswarmcreatepointpercellcount_(DM dm,PetscInt *ncells,PetscInt **count, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(ncells);
CHKFORTRANNULLINTEGER(count);
*ierr = DMSwarmCreatePointPerCellCount(
	(DM)PetscToPointer((dm) ),ncells,count);
}
PETSC_EXTERN void  dmswarmgetnumspecies_(DM sw,PetscInt *Ns, int *ierr)
{
CHKFORTRANNULLOBJECT(sw);
CHKFORTRANNULLINTEGER(Ns);
*ierr = DMSwarmGetNumSpecies(
	(DM)PetscToPointer((sw) ),Ns);
}
PETSC_EXTERN void  dmswarmsetnumspecies_(DM sw,PetscInt *Ns, int *ierr)
{
CHKFORTRANNULLOBJECT(sw);
*ierr = DMSwarmSetNumSpecies(
	(DM)PetscToPointer((sw) ),*Ns);
}
PETSC_EXTERN void  dmswarmcomputelocalsizefromoptions_(DM sw, int *ierr)
{
CHKFORTRANNULLOBJECT(sw);
*ierr = DMSwarmComputeLocalSizeFromOptions(
	(DM)PetscToPointer((sw) ));
}
PETSC_EXTERN void  dmswarminitializecoordinates_(DM sw, int *ierr)
{
CHKFORTRANNULLOBJECT(sw);
*ierr = DMSwarmInitializeCoordinates(
	(DM)PetscToPointer((sw) ));
}
PETSC_EXTERN void  dmswarminitializevelocitiesfromoptions_(DM sw, PetscReal v0[], int *ierr)
{
CHKFORTRANNULLOBJECT(sw);
CHKFORTRANNULLREAL(v0);
*ierr = DMSwarmInitializeVelocitiesFromOptions(
	(DM)PetscToPointer((sw) ),v0);
}
#if defined(__cplusplus)
}
#endif
