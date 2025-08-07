#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmlocalts.c */
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
#define dmtscreaterhsmassmatrix_ DMTSCREATERHSMASSMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmtscreaterhsmassmatrix_ dmtscreaterhsmassmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmtscreaterhsmassmatrixlumped_ DMTSCREATERHSMASSMATRIXLUMPED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmtscreaterhsmassmatrixlumped_ dmtscreaterhsmassmatrixlumped
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmtsdestroyrhsmassmatrix_ DMTSDESTROYRHSMASSMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmtsdestroyrhsmassmatrix_ dmtsdestroyrhsmassmatrix
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmtscreaterhsmassmatrix_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMTSCreateRHSMassMatrix(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmtscreaterhsmassmatrixlumped_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMTSCreateRHSMassMatrixLumped(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmtsdestroyrhsmassmatrix_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMTSDestroyRHSMassMatrix(
	(DM)PetscToPointer((dm) ));
}
#if defined(__cplusplus)
}
#endif
