#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* filev.c */
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
#define petscviewerasciisettab_ PETSCVIEWERASCIISETTAB
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciisettab_ petscviewerasciisettab
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerasciigettab_ PETSCVIEWERASCIIGETTAB
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciigettab_ petscviewerasciigettab
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerasciiaddtab_ PETSCVIEWERASCIIADDTAB
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciiaddtab_ petscviewerasciiaddtab
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerasciisubtracttab_ PETSCVIEWERASCIISUBTRACTTAB
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciisubtracttab_ petscviewerasciisubtracttab
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerasciipushsynchronized_ PETSCVIEWERASCIIPUSHSYNCHRONIZED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciipushsynchronized_ petscviewerasciipushsynchronized
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerasciipopsynchronized_ PETSCVIEWERASCIIPOPSYNCHRONIZED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciipopsynchronized_ petscviewerasciipopsynchronized
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerasciipushtab_ PETSCVIEWERASCIIPUSHTAB
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciipushtab_ petscviewerasciipushtab
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerasciipoptab_ PETSCVIEWERASCIIPOPTAB
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciipoptab_ petscviewerasciipoptab
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerasciiusetabs_ PETSCVIEWERASCIIUSETABS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciiusetabs_ petscviewerasciiusetabs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerasciigetstdout_ PETSCVIEWERASCIIGETSTDOUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerasciigetstdout_ petscviewerasciigetstdout
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerfilesetname_ PETSCVIEWERFILESETNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerfilesetname_ petscviewerfilesetname
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewerasciisettab_(PetscViewer viewer,PetscInt *tabs, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerASCIISetTab(PetscPatchDefaultViewers((PetscViewer*)viewer),*tabs);
}
PETSC_EXTERN void  petscviewerasciigettab_(PetscViewer viewer,PetscInt *tabs, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLINTEGER(tabs);
*ierr = PetscViewerASCIIGetTab(PetscPatchDefaultViewers((PetscViewer*)viewer),tabs);
}
PETSC_EXTERN void  petscviewerasciiaddtab_(PetscViewer viewer,PetscInt *tabs, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerASCIIAddTab(PetscPatchDefaultViewers((PetscViewer*)viewer),*tabs);
}
PETSC_EXTERN void  petscviewerasciisubtracttab_(PetscViewer viewer,PetscInt *tabs, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerASCIISubtractTab(PetscPatchDefaultViewers((PetscViewer*)viewer),*tabs);
}
PETSC_EXTERN void  petscviewerasciipushsynchronized_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerASCIIPushSynchronized(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewerasciipopsynchronized_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerASCIIPopSynchronized(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewerasciipushtab_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerASCIIPushTab(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewerasciipoptab_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerASCIIPopTab(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewerasciiusetabs_(PetscViewer viewer,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerASCIIUseTabs(PetscPatchDefaultViewers((PetscViewer*)viewer),*flg);
}
PETSC_EXTERN void  petscviewerasciigetstdout_(MPI_Fint * comm,PetscViewer *viewer, int *ierr)
{
PetscBool viewer_null = !*(void**) viewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerASCIIGetStdout(
	MPI_Comm_f2c(*(comm)),viewer);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! viewer_null && !*(void**) viewer) * (void **) viewer = (void *)-2;
}
PETSC_EXTERN void  petscviewerfilesetname_(PetscViewer viewer, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerFileSetName(PetscPatchDefaultViewers((PetscViewer*)viewer),_cltmp0);
  FREECHAR(name,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
