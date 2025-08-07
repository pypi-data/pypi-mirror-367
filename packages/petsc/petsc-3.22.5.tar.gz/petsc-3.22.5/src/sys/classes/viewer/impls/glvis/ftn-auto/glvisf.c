#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* glvis.c */
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
#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerglvissetprecision_ PETSCVIEWERGLVISSETPRECISION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerglvissetprecision_ petscviewerglvissetprecision
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerglvissetsnapid_ PETSCVIEWERGLVISSETSNAPID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerglvissetsnapid_ petscviewerglvissetsnapid
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerglvisopen_ PETSCVIEWERGLVISOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerglvisopen_ petscviewerglvisopen
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewerglvissetprecision_(PetscViewer viewer,PetscInt *prec, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerGLVisSetPrecision(PetscPatchDefaultViewers((PetscViewer*)viewer),*prec);
}
PETSC_EXTERN void  petscviewerglvissetsnapid_(PetscViewer viewer,PetscInt *id, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerGLVisSetSnapId(PetscPatchDefaultViewers((PetscViewer*)viewer),*id);
}
PETSC_EXTERN void  petscviewerglvisopen_(MPI_Fint * comm,PetscViewerGLVisType *type, char name[],PetscInt *port,PetscViewer *viewer, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool viewer_null = !*(void**) viewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerGLVisOpen(
	MPI_Comm_f2c(*(comm)),*type,_cltmp0,*port,viewer);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! viewer_null && !*(void**) viewer) * (void **) viewer = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
