#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dtweakform.c */
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

#include "petscds.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscweakformcopy_ PETSCWEAKFORMCOPY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscweakformcopy_ petscweakformcopy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscweakformclear_ PETSCWEAKFORMCLEAR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscweakformclear_ petscweakformclear
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscweakformrewritekeys_ PETSCWEAKFORMREWRITEKEYS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscweakformrewritekeys_ petscweakformrewritekeys
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscweakformreplacelabel_ PETSCWEAKFORMREPLACELABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscweakformreplacelabel_ petscweakformreplacelabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscweakformgetnumfields_ PETSCWEAKFORMGETNUMFIELDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscweakformgetnumfields_ petscweakformgetnumfields
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscweakformsetnumfields_ PETSCWEAKFORMSETNUMFIELDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscweakformsetnumfields_ petscweakformsetnumfields
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscweakformdestroy_ PETSCWEAKFORMDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscweakformdestroy_ petscweakformdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscweakformview_ PETSCWEAKFORMVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscweakformview_ petscweakformview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscweakformcreate_ PETSCWEAKFORMCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscweakformcreate_ petscweakformcreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscweakformcopy_(PetscWeakForm wf,PetscWeakForm wfNew, int *ierr)
{
CHKFORTRANNULLOBJECT(wf);
CHKFORTRANNULLOBJECT(wfNew);
*ierr = PetscWeakFormCopy(
	(PetscWeakForm)PetscToPointer((wf) ),
	(PetscWeakForm)PetscToPointer((wfNew) ));
}
PETSC_EXTERN void  petscweakformclear_(PetscWeakForm wf, int *ierr)
{
CHKFORTRANNULLOBJECT(wf);
*ierr = PetscWeakFormClear(
	(PetscWeakForm)PetscToPointer((wf) ));
}
PETSC_EXTERN void  petscweakformrewritekeys_(PetscWeakForm wf,DMLabel label,PetscInt *Nv, PetscInt values[], int *ierr)
{
CHKFORTRANNULLOBJECT(wf);
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(values);
*ierr = PetscWeakFormRewriteKeys(
	(PetscWeakForm)PetscToPointer((wf) ),
	(DMLabel)PetscToPointer((label) ),*Nv,values);
}
PETSC_EXTERN void  petscweakformreplacelabel_(PetscWeakForm wf,DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(wf);
CHKFORTRANNULLOBJECT(label);
*ierr = PetscWeakFormReplaceLabel(
	(PetscWeakForm)PetscToPointer((wf) ),
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  petscweakformgetnumfields_(PetscWeakForm wf,PetscInt *Nf, int *ierr)
{
CHKFORTRANNULLOBJECT(wf);
CHKFORTRANNULLINTEGER(Nf);
*ierr = PetscWeakFormGetNumFields(
	(PetscWeakForm)PetscToPointer((wf) ),Nf);
}
PETSC_EXTERN void  petscweakformsetnumfields_(PetscWeakForm wf,PetscInt *Nf, int *ierr)
{
CHKFORTRANNULLOBJECT(wf);
*ierr = PetscWeakFormSetNumFields(
	(PetscWeakForm)PetscToPointer((wf) ),*Nf);
}
PETSC_EXTERN void  petscweakformdestroy_(PetscWeakForm *wf, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(wf);
 PetscBool wf_null = !*(void**) wf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(wf);
*ierr = PetscWeakFormDestroy(wf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! wf_null && !*(void**) wf) * (void **) wf = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(wf);
 }
PETSC_EXTERN void  petscweakformview_(PetscWeakForm wf,PetscViewer v, int *ierr)
{
CHKFORTRANNULLOBJECT(wf);
CHKFORTRANNULLOBJECT(v);
*ierr = PetscWeakFormView(
	(PetscWeakForm)PetscToPointer((wf) ),PetscPatchDefaultViewers((PetscViewer*)v));
}
PETSC_EXTERN void  petscweakformcreate_(MPI_Fint * comm,PetscWeakForm *wf, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(wf);
 PetscBool wf_null = !*(void**) wf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(wf);
*ierr = PetscWeakFormCreate(
	MPI_Comm_f2c(*(comm)),wf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! wf_null && !*(void**) wf) * (void **) wf = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
