#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* networkmonitor.c */
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

#include "petscdmnetwork.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkmonitorcreate_ DMNETWORKMONITORCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkmonitorcreate_ dmnetworkmonitorcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkmonitordestroy_ DMNETWORKMONITORDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkmonitordestroy_ dmnetworkmonitordestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkmonitorpop_ DMNETWORKMONITORPOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkmonitorpop_ dmnetworkmonitorpop
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmnetworkmonitorcreate_(DM network,DMNetworkMonitor *monitorptr, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(monitorptr);
 CHKFORTRANNULLOBJECT(network);
PetscBool monitorptr_null = !*(void**) monitorptr ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(monitorptr);
*ierr = DMNetworkMonitorCreate(
	(DM)PetscToPointer((network) ),monitorptr);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! monitorptr_null && !*(void**) monitorptr) * (void **) monitorptr = (void *)-2;
}
PETSC_EXTERN void  dmnetworkmonitordestroy_(DMNetworkMonitor *monitor, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(monitor);
 PetscBool monitor_null = !*(void**) monitor ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(monitor);
*ierr = DMNetworkMonitorDestroy(monitor);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! monitor_null && !*(void**) monitor) * (void **) monitor = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(monitor);
 }
PETSC_EXTERN void  dmnetworkmonitorpop_(DMNetworkMonitor monitor, int *ierr)
{
CHKFORTRANNULLOBJECT(monitor);
*ierr = DMNetworkMonitorPop(
	(DMNetworkMonitor)PetscToPointer((monitor) ));
}
#if defined(__cplusplus)
}
#endif
