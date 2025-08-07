#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmgenerate.c */
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
#define dmadaptlabel_ DMADAPTLABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptlabel_ dmadaptlabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptmetric_ DMADAPTMETRIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptmetric_ dmadaptmetric
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmadaptlabel_(DM dm,DMLabel label,DM *dmAdapt, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
PetscBool dmAdapt_null = !*(void**) dmAdapt ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmAdapt);
*ierr = DMAdaptLabel(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ),dmAdapt);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmAdapt_null && !*(void**) dmAdapt) * (void **) dmAdapt = (void *)-2;
}
PETSC_EXTERN void  dmadaptmetric_(DM dm,Vec metric,DMLabel bdLabel,DMLabel rgLabel,DM *dmAdapt, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(metric);
CHKFORTRANNULLOBJECT(bdLabel);
CHKFORTRANNULLOBJECT(rgLabel);
PetscBool dmAdapt_null = !*(void**) dmAdapt ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmAdapt);
*ierr = DMAdaptMetric(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((metric) ),
	(DMLabel)PetscToPointer((bdLabel) ),
	(DMLabel)PetscToPointer((rgLabel) ),dmAdapt);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmAdapt_null && !*(void**) dmAdapt) * (void **) dmAdapt = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
