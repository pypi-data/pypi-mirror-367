#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* device.cxx */
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

#include <petscdevice.h>
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdeviceview_ PETSCDEVICEVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdeviceview_ petscdeviceview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdevicegettype_ PETSCDEVICEGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdevicegettype_ petscdevicegettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdeviceview_(PetscDevice device,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(device);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscDeviceView(
	(PetscDevice)PetscToPointer((device) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscdevicegettype_(PetscDevice device,PetscDeviceType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(device);
*ierr = PetscDeviceGetType(
	(PetscDevice)PetscToPointer((device) ),type);
}
#if defined(__cplusplus)
}
#endif
