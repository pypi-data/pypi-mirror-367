#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* vtkv.c */
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
#define petscviewervtkgetdm_ PETSCVIEWERVTKGETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewervtkgetdm_ petscviewervtkgetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewervtkopen_ PETSCVIEWERVTKOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewervtkopen_ petscviewervtkopen
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewervtkgetdm_(PetscViewer viewer,PetscObject *dm, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = PetscViewerVTKGetDM(PetscPatchDefaultViewers((PetscViewer*)viewer),dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  petscviewervtkopen_(MPI_Fint * comm, char name[],PetscFileMode *type,PetscViewer *vtk, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool vtk_null = !*(void**) vtk ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vtk);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerVTKOpen(
	MPI_Comm_f2c(*(comm)),_cltmp0,*type,vtk);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vtk_null && !*(void**) vtk) * (void **) vtk = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
