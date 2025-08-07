#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* viewa.c */
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

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerpushformat_ PETSCVIEWERPUSHFORMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerpushformat_ petscviewerpushformat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerpopformat_ PETSCVIEWERPOPFORMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerpopformat_ petscviewerpopformat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewergetformat_ PETSCVIEWERGETFORMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewergetformat_ petscviewergetformat
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewerpushformat_(PetscViewer viewer,PetscViewerFormat *format, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerPushFormat(PetscPatchDefaultViewers((PetscViewer*)viewer),*format);
}
PETSC_EXTERN void  petscviewerpopformat_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerPopFormat(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewergetformat_(PetscViewer viewer,PetscViewerFormat *format, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerGetFormat(PetscPatchDefaultViewers((PetscViewer*)viewer),format);
}
#if defined(__cplusplus)
}
#endif
