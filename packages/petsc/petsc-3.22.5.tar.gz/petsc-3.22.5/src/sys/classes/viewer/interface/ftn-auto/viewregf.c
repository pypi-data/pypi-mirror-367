#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* viewreg.c */
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
#define petscoptionspushcreatevieweroff_ PETSCOPTIONSPUSHCREATEVIEWEROFF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionspushcreatevieweroff_ petscoptionspushcreatevieweroff
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionspopcreatevieweroff_ PETSCOPTIONSPOPCREATEVIEWEROFF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionspopcreatevieweroff_ petscoptionspopcreatevieweroff
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsgetcreatevieweroff_ PETSCOPTIONSGETCREATEVIEWEROFF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsgetcreatevieweroff_ petscoptionsgetcreatevieweroff
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewercreate_ PETSCVIEWERCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewercreate_ petscviewercreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewersettype_ PETSCVIEWERSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewersettype_ petscviewersettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscoptionspushcreatevieweroff_(PetscBool *flg, int *ierr)
{
*ierr = PetscOptionsPushCreateViewerOff(*flg);
}
PETSC_EXTERN void  petscoptionspopcreatevieweroff_(int *ierr)
{
*ierr = PetscOptionsPopCreateViewerOff();
}
PETSC_EXTERN void  petscoptionsgetcreatevieweroff_(PetscBool *flg, int *ierr)
{
*ierr = PetscOptionsGetCreateViewerOff(flg);
}
PETSC_EXTERN void  petscviewercreate_(MPI_Fint * comm,PetscViewer *inviewer, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(inviewer);
 PetscBool inviewer_null = !*(void**) inviewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(inviewer);
*ierr = PetscViewerCreate(
	MPI_Comm_f2c(*(comm)),inviewer);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! inviewer_null && !*(void**) inviewer) * (void **) inviewer = (void *)-2;
}
PETSC_EXTERN void  petscviewersettype_(PetscViewer viewer,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = PetscViewerSetType(PetscPatchDefaultViewers((PetscViewer*)viewer),_cltmp0);
  FREECHAR(type,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
