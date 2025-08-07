#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* vmatlab.c */
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
#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewermatlabputarray_ PETSCVIEWERMATLABPUTARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewermatlabputarray_ petscviewermatlabputarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewermatlabgetarray_ PETSCVIEWERMATLABGETARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewermatlabgetarray_ petscviewermatlabgetarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewermatlabopen_ PETSCVIEWERMATLABOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewermatlabopen_ petscviewermatlabopen
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewermatlabputarray_(PetscViewer mfile,int *m,int *n, PetscScalar *array, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mfile);
CHKFORTRANNULLSCALAR(array);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerMatlabPutArray(PetscPatchDefaultViewers((PetscViewer*)mfile),*m,*n,array,_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscviewermatlabgetarray_(PetscViewer mfile,int *m,int *n,PetscScalar array[], char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mfile);
CHKFORTRANNULLSCALAR(array);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerMatlabGetArray(PetscPatchDefaultViewers((PetscViewer*)mfile),*m,*n,array,_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscviewermatlabopen_(MPI_Fint * comm, char name[],PetscFileMode *type,PetscViewer *binv, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool binv_null = !*(void**) binv ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(binv);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerMatlabOpen(
	MPI_Comm_f2c(*(comm)),_cltmp0,*type,binv);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! binv_null && !*(void**) binv) * (void **) binv = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
