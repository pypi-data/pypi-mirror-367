#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dupl.c */
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

#include "petscviewer.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewergetsubviewer_ PETSCVIEWERGETSUBVIEWER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewergetsubviewer_ petscviewergetsubviewer
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerrestoresubviewer_ PETSCVIEWERRESTORESUBVIEWER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerrestoresubviewer_ petscviewerrestoresubviewer
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewergetsubviewer_(PetscViewer viewer,MPI_Fint * comm,PetscViewer *outviewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
PetscBool outviewer_null = !*(void**) outviewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(outviewer);
*ierr = PetscViewerGetSubViewer(PetscPatchDefaultViewers((PetscViewer*)viewer),
	MPI_Comm_f2c(*(comm)),outviewer);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! outviewer_null && !*(void**) outviewer) * (void **) outviewer = (void *)-2;
}
PETSC_EXTERN void  petscviewerrestoresubviewer_(PetscViewer viewer,MPI_Fint * comm,PetscViewer *outviewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
PetscBool outviewer_null = !*(void**) outviewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(outviewer);
*ierr = PetscViewerRestoreSubViewer(PetscPatchDefaultViewers((PetscViewer*)viewer),
	MPI_Comm_f2c(*(comm)),outviewer);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! outviewer_null && !*(void**) outviewer) * (void **) outviewer = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
