#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* composite.c */
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

#include "petscksp.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pccompositesettype_ PCCOMPOSITESETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pccompositesettype_ pccompositesettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pccompositegettype_ PCCOMPOSITEGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pccompositegettype_ pccompositegettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pccompositespecialsetalpha_ PCCOMPOSITESPECIALSETALPHA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pccompositespecialsetalpha_ pccompositespecialsetalpha
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pccompositeaddpc_ PCCOMPOSITEADDPC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pccompositeaddpc_ pccompositeaddpc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pccompositegetnumberpc_ PCCOMPOSITEGETNUMBERPC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pccompositegetnumberpc_ pccompositegetnumberpc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pccompositegetpc_ PCCOMPOSITEGETPC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pccompositegetpc_ pccompositegetpc
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pccompositesettype_(PC pc,PCCompositeType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCCompositeSetType(
	(PC)PetscToPointer((pc) ),*type);
}
PETSC_EXTERN void  pccompositegettype_(PC pc,PCCompositeType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCCompositeGetType(
	(PC)PetscToPointer((pc) ),type);
}
PETSC_EXTERN void  pccompositespecialsetalpha_(PC pc,PetscScalar *alpha, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCCompositeSpecialSetAlpha(
	(PC)PetscToPointer((pc) ),*alpha);
}
PETSC_EXTERN void  pccompositeaddpc_(PC pc,PC subpc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(subpc);
*ierr = PCCompositeAddPC(
	(PC)PetscToPointer((pc) ),
	(PC)PetscToPointer((subpc) ));
}
PETSC_EXTERN void  pccompositegetnumberpc_(PC pc,PetscInt *num, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLINTEGER(num);
*ierr = PCCompositeGetNumberPC(
	(PC)PetscToPointer((pc) ),num);
}
PETSC_EXTERN void  pccompositegetpc_(PC pc,PetscInt *n,PC *subpc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool subpc_null = !*(void**) subpc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subpc);
*ierr = PCCompositeGetPC(
	(PC)PetscToPointer((pc) ),*n,subpc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subpc_null && !*(void**) subpc) * (void **) subpc = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
