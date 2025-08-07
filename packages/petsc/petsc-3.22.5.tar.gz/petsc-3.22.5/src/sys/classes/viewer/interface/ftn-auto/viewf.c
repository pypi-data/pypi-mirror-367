#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* view.c */
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
#define petscviewerdestroy_ PETSCVIEWERDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdestroy_ petscviewerdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewergettype_ PETSCVIEWERGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewergettype_ petscviewergettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewersetoptionsprefix_ PETSCVIEWERSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewersetoptionsprefix_ petscviewersetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerappendoptionsprefix_ PETSCVIEWERAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerappendoptionsprefix_ petscviewerappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewergetoptionsprefix_ PETSCVIEWERGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewergetoptionsprefix_ petscviewergetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewersetup_ PETSCVIEWERSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewersetup_ petscviewersetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerviewfromoptions_ PETSCVIEWERVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerviewfromoptions_ petscviewerviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerview_ PETSCVIEWERVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerview_ petscviewerview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerreadable_ PETSCVIEWERREADABLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerreadable_ petscviewerreadable
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerwritable_ PETSCVIEWERWRITABLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerwritable_ petscviewerwritable
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewercheckreadable_ PETSCVIEWERCHECKREADABLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewercheckreadable_ petscviewercheckreadable
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewercheckwritable_ PETSCVIEWERCHECKWRITABLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewercheckwritable_ petscviewercheckwritable
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewerdestroy_(PetscViewer *viewer, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(viewer);
 PetscBool viewer_null = !*(void**) viewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerDestroy(viewer);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! viewer_null && !*(void**) viewer) * (void **) viewer = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(viewer);
 }
PETSC_EXTERN void  petscviewergettype_(PetscViewer viewer,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerGetType(PetscPatchDefaultViewers((PetscViewer*)viewer),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  petscviewersetoptionsprefix_(PetscViewer viewer, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscViewerSetOptionsPrefix(PetscPatchDefaultViewers((PetscViewer*)viewer),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  petscviewerappendoptionsprefix_(PetscViewer viewer, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscViewerAppendOptionsPrefix(PetscPatchDefaultViewers((PetscViewer*)viewer),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  petscviewergetoptionsprefix_(PetscViewer viewer, char *prefix, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerGetOptionsPrefix(PetscPatchDefaultViewers((PetscViewer*)viewer),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for prefix */
*ierr = PetscStrncpy(prefix, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, prefix, cl0);
}
PETSC_EXTERN void  petscviewersetup_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerSetUp(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewerviewfromoptions_(PetscViewer A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerViewFromOptions(PetscPatchDefaultViewers((PetscViewer*)A),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscviewerview_(PetscViewer v,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerView(PetscPatchDefaultViewers((PetscViewer*)v),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewerreadable_(PetscViewer viewer,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerReadable(PetscPatchDefaultViewers((PetscViewer*)viewer),flg);
}
PETSC_EXTERN void  petscviewerwritable_(PetscViewer viewer,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerWritable(PetscPatchDefaultViewers((PetscViewer*)viewer),flg);
}
PETSC_EXTERN void  petscviewercheckreadable_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerCheckReadable(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewercheckwritable_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerCheckWritable(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
#if defined(__cplusplus)
}
#endif
