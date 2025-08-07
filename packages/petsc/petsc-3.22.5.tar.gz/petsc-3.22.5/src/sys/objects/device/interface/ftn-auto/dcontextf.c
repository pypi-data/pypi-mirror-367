#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dcontext.cxx */
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
#define petscdevicecontextview_ PETSCDEVICECONTEXTVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdevicecontextview_ petscdevicecontextview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdevicecontextviewfromoptions_ PETSCDEVICECONTEXTVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdevicecontextviewfromoptions_ petscdevicecontextviewfromoptions
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdevicecontextview_(PetscDeviceContext dctx,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(dctx);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscDeviceContextView(
	(PetscDeviceContext)PetscToPointer((dctx) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscdevicecontextviewfromoptions_(PetscDeviceContext dctx,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dctx);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscDeviceContextViewFromOptions(
	(PetscDeviceContext)PetscToPointer((dctx) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
