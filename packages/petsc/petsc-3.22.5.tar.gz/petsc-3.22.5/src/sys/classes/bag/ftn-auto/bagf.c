#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* bag.c */
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

#include "petscbag.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbagdestroy_ PETSCBAGDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbagdestroy_ petscbagdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbagsetfromoptions_ PETSCBAGSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbagsetfromoptions_ petscbagsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbagview_ PETSCBAGVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbagview_ petscbagview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbagviewfromoptions_ PETSCBAGVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbagviewfromoptions_ petscbagviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbagload_ PETSCBAGLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbagload_ petscbagload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbagsetname_ PETSCBAGSETNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbagsetname_ petscbagsetname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbagsetoptionsprefix_ PETSCBAGSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbagsetoptionsprefix_ petscbagsetoptionsprefix
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscbagdestroy_(PetscBag *bag, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(bag);
 PetscBool bag_null = !*(void**) bag ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(bag);
*ierr = PetscBagDestroy(bag);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! bag_null && !*(void**) bag) * (void **) bag = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(bag);
 }
PETSC_EXTERN void  petscbagsetfromoptions_(PetscBag bag, int *ierr)
{
CHKFORTRANNULLOBJECT(bag);
*ierr = PetscBagSetFromOptions(
	(PetscBag)PetscToPointer((bag) ));
}
PETSC_EXTERN void  petscbagview_(PetscBag bag,PetscViewer view, int *ierr)
{
CHKFORTRANNULLOBJECT(bag);
CHKFORTRANNULLOBJECT(view);
*ierr = PetscBagView(
	(PetscBag)PetscToPointer((bag) ),PetscPatchDefaultViewers((PetscViewer*)view));
}
PETSC_EXTERN void  petscbagviewfromoptions_(PetscBag bag,PetscObject bobj, char optionname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(bag);
CHKFORTRANNULLOBJECT(bobj);
/* insert Fortran-to-C conversion for optionname */
  FIXCHAR(optionname,cl0,_cltmp0);
*ierr = PetscBagViewFromOptions(
	(PetscBag)PetscToPointer((bag) ),
	(PetscObject)PetscToPointer((bobj) ),_cltmp0);
  FREECHAR(optionname,_cltmp0);
}
PETSC_EXTERN void  petscbagload_(PetscViewer view,PetscBag bag, int *ierr)
{
CHKFORTRANNULLOBJECT(view);
CHKFORTRANNULLOBJECT(bag);
*ierr = PetscBagLoad(PetscPatchDefaultViewers((PetscViewer*)view),
	(PetscBag)PetscToPointer((bag) ));
}
PETSC_EXTERN void  petscbagsetname_(PetscBag bag, char *name, char *help, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(bag);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
/* insert Fortran-to-C conversion for help */
  FIXCHAR(help,cl1,_cltmp1);
*ierr = PetscBagSetName(
	(PetscBag)PetscToPointer((bag) ),_cltmp0,_cltmp1);
  FREECHAR(name,_cltmp0);
  FREECHAR(help,_cltmp1);
}
PETSC_EXTERN void  petscbagsetoptionsprefix_(PetscBag bag, char pre[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(bag);
/* insert Fortran-to-C conversion for pre */
  FIXCHAR(pre,cl0,_cltmp0);
*ierr = PetscBagSetOptionsPrefix(
	(PetscBag)PetscToPointer((bag) ),_cltmp0);
  FREECHAR(pre,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
