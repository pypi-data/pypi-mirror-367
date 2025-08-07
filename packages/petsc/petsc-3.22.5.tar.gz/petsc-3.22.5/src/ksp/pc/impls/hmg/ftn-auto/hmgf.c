#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* hmg.c */
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
#define pchmgsetreuseinterpolation_ PCHMGSETREUSEINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchmgsetreuseinterpolation_ pchmgsetreuseinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchmgsetusesubspacecoarsening_ PCHMGSETUSESUBSPACECOARSENING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchmgsetusesubspacecoarsening_ pchmgsetusesubspacecoarsening
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchmgsetinnerpctype_ PCHMGSETINNERPCTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchmgsetinnerpctype_ pchmgsetinnerpctype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchmgsetcoarseningcomponent_ PCHMGSETCOARSENINGCOMPONENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchmgsetcoarseningcomponent_ pchmgsetcoarseningcomponent
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchmgusematmaij_ PCHMGUSEMATMAIJ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchmgusematmaij_ pchmgusematmaij
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pchmgsetreuseinterpolation_(PC pc,PetscBool *reuse, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCHMGSetReuseInterpolation(
	(PC)PetscToPointer((pc) ),*reuse);
}
PETSC_EXTERN void  pchmgsetusesubspacecoarsening_(PC pc,PetscBool *subspace, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCHMGSetUseSubspaceCoarsening(
	(PC)PetscToPointer((pc) ),*subspace);
}
PETSC_EXTERN void  pchmgsetinnerpctype_(PC pc,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = PCHMGSetInnerPCType(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  pchmgsetcoarseningcomponent_(PC pc,PetscInt *component, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCHMGSetCoarseningComponent(
	(PC)PetscToPointer((pc) ),*component);
}
PETSC_EXTERN void  pchmgusematmaij_(PC pc,PetscBool *usematmaij, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCHMGUseMatMAIJ(
	(PC)PetscToPointer((pc) ),*usematmaij);
}
#if defined(__cplusplus)
}
#endif
