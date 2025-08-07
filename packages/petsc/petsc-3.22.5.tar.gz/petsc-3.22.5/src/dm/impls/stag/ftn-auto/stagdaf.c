#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* stagda.c */
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
#include "petscdmstag.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagvecsplittodmda_ DMSTAGVECSPLITTODMDA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagvecsplittodmda_ dmstagvecsplittodmda
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmstagvecsplittodmda_(DM dm,Vec vec,DMStagStencilLocation *loc,PetscInt *c,DM *pda,Vec *pdavec, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(vec);
PetscBool pda_null = !*(void**) pda ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pda);
PetscBool pdavec_null = !*(void**) pdavec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pdavec);
*ierr = DMStagVecSplitToDMDA(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((vec) ),*loc,*c,pda,pdavec);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pda_null && !*(void**) pda) * (void **) pda = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pdavec_null && !*(void**) pdavec) * (void **) pdavec = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
