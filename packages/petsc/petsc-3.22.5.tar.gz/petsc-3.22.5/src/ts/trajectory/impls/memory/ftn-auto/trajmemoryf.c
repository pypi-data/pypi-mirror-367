#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* trajmemory.c */
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
#define tstrajectorymemorysettype_ TSTRAJECTORYMEMORYSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorymemorysettype_ tstrajectorymemorysettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetmaxcpsram_ TSTRAJECTORYSETMAXCPSRAM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetmaxcpsram_ tstrajectorysetmaxcpsram
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetmaxcpsdisk_ TSTRAJECTORYSETMAXCPSDISK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetmaxcpsdisk_ tstrajectorysetmaxcpsdisk
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetmaxunitsram_ TSTRAJECTORYSETMAXUNITSRAM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetmaxunitsram_ tstrajectorysetmaxunitsram
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetmaxunitsdisk_ TSTRAJECTORYSETMAXUNITSDISK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetmaxunitsdisk_ tstrajectorysetmaxunitsdisk
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tstrajectorymemorysettype_(TSTrajectory tj,TSTrajectoryMemoryType *tj_memory_type, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectoryMemorySetType(
	(TSTrajectory)PetscToPointer((tj) ),*tj_memory_type);
}
PETSC_EXTERN void  tstrajectorysetmaxcpsram_(TSTrajectory tj,PetscInt *max_cps_ram, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectorySetMaxCpsRAM(
	(TSTrajectory)PetscToPointer((tj) ),*max_cps_ram);
}
PETSC_EXTERN void  tstrajectorysetmaxcpsdisk_(TSTrajectory tj,PetscInt *max_cps_disk, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectorySetMaxCpsDisk(
	(TSTrajectory)PetscToPointer((tj) ),*max_cps_disk);
}
PETSC_EXTERN void  tstrajectorysetmaxunitsram_(TSTrajectory tj,PetscInt *max_units_ram, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectorySetMaxUnitsRAM(
	(TSTrajectory)PetscToPointer((tj) ),*max_units_ram);
}
PETSC_EXTERN void  tstrajectorysetmaxunitsdisk_(TSTrajectory tj,PetscInt *max_units_disk, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectorySetMaxUnitsDisk(
	(TSTrajectory)PetscToPointer((tj) ),*max_units_disk);
}
#if defined(__cplusplus)
}
#endif
