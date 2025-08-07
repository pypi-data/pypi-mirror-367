#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* agg.c */
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

#include "petscpc.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetnsmooths_ PCGAMGSETNSMOOTHS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetnsmooths_ pcgamgsetnsmooths
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetaggressivelevels_ PCGAMGSETAGGRESSIVELEVELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetaggressivelevels_ pcgamgsetaggressivelevels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgmisksetaggressive_ PCGAMGMISKSETAGGRESSIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgmisksetaggressive_ pcgamgmisksetaggressive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetaggressivesquaregraph_ PCGAMGSETAGGRESSIVESQUAREGRAPH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetaggressivesquaregraph_ pcgamgsetaggressivesquaregraph
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgmisksetmindegreeordering_ PCGAMGMISKSETMINDEGREEORDERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgmisksetmindegreeordering_ pcgamgmisksetmindegreeordering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetlowmemoryfilter_ PCGAMGSETLOWMEMORYFILTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetlowmemoryfilter_ pcgamgsetlowmemoryfilter
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetgraphsymmetrize_ PCGAMGSETGRAPHSYMMETRIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetgraphsymmetrize_ pcgamgsetgraphsymmetrize
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcgamgsetnsmooths_(PC pc,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetNSmooths(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcgamgsetaggressivelevels_(PC pc,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetAggressiveLevels(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcgamgmisksetaggressive_(PC pc,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGMISkSetAggressive(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcgamgsetaggressivesquaregraph_(PC pc,PetscBool *b, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetAggressiveSquareGraph(
	(PC)PetscToPointer((pc) ),*b);
}
PETSC_EXTERN void  pcgamgmisksetmindegreeordering_(PC pc,PetscBool *b, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGMISkSetMinDegreeOrdering(
	(PC)PetscToPointer((pc) ),*b);
}
PETSC_EXTERN void  pcgamgsetlowmemoryfilter_(PC pc,PetscBool *b, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetLowMemoryFilter(
	(PC)PetscToPointer((pc) ),*b);
}
PETSC_EXTERN void  pcgamgsetgraphsymmetrize_(PC pc,PetscBool *b, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetGraphSymmetrize(
	(PC)PetscToPointer((pc) ),*b);
}
#if defined(__cplusplus)
}
#endif
