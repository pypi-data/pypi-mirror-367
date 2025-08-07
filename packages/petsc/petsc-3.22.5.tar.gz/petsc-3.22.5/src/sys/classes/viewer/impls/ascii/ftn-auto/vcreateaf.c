#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* vcreatea.c */
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
#define petscviewerasciigetstderr_ PETSCVIEWERASCIIGETSTDERR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciigetstderr_ petscviewerasciigetstderr
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerasciiopen_ PETSCVIEWERASCIIOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciiopen_ petscviewerasciiopen
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewerasciigetstderr_(MPI_Fint * comm,PetscViewer *viewer, int *ierr)
{
PetscBool viewer_null = !*(void**) viewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerASCIIGetStderr(
	MPI_Comm_f2c(*(comm)),viewer);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! viewer_null && !*(void**) viewer) * (void **) viewer = (void *)-2;
}
PETSC_EXTERN void  petscviewerasciiopen_(MPI_Fint * comm, char name[],PetscViewer *viewer, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool viewer_null = !*(void**) viewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerASCIIOpen(
	MPI_Comm_f2c(*(comm)),_cltmp0,viewer);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! viewer_null && !*(void**) viewer) * (void **) viewer = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
