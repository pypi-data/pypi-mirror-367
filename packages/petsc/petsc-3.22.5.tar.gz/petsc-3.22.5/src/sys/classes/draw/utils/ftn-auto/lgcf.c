#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* lgc.c */
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

#include "petscdraw.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlggetaxis_ PETSCDRAWLGGETAXIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlggetaxis_ petscdrawlggetaxis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlggetdraw_ PETSCDRAWLGGETDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlggetdraw_ petscdrawlggetdraw
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgspdraw_ PETSCDRAWLGSPDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgspdraw_ petscdrawlgspdraw
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgcreate_ PETSCDRAWLGCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgcreate_ petscdrawlgcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgsetcolors_ PETSCDRAWLGSETCOLORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgsetcolors_ petscdrawlgsetcolors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlggetdimension_ PETSCDRAWLGGETDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlggetdimension_ petscdrawlggetdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgsetdimension_ PETSCDRAWLGSETDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgsetdimension_ petscdrawlgsetdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgsetlimits_ PETSCDRAWLGSETLIMITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgsetlimits_ petscdrawlgsetlimits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgreset_ PETSCDRAWLGRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgreset_ petscdrawlgreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgdestroy_ PETSCDRAWLGDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgdestroy_ petscdrawlgdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgsetusemarkers_ PETSCDRAWLGSETUSEMARKERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgsetusemarkers_ petscdrawlgsetusemarkers
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgdraw_ PETSCDRAWLGDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgdraw_ petscdrawlgdraw
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgsave_ PETSCDRAWLGSAVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgsave_ petscdrawlgsave
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgview_ PETSCDRAWLGVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgview_ petscdrawlgview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgsetoptionsprefix_ PETSCDRAWLGSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgsetoptionsprefix_ petscdrawlgsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawlgsetfromoptions_ PETSCDRAWLGSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawlgsetfromoptions_ petscdrawlgsetfromoptions
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawlggetaxis_(PetscDrawLG lg,PetscDrawAxis *axis, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
PetscBool axis_null = !*(void**) axis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(axis);
*ierr = PetscDrawLGGetAxis(
	(PetscDrawLG)PetscToPointer((lg) ),axis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! axis_null && !*(void**) axis) * (void **) axis = (void *)-2;
}
PETSC_EXTERN void  petscdrawlggetdraw_(PetscDrawLG lg,PetscDraw *draw, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
PetscBool draw_null = !*(void**) draw ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawLGGetDraw(
	(PetscDrawLG)PetscToPointer((lg) ),draw);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! draw_null && !*(void**) draw) * (void **) draw = (void *)-2;
}
PETSC_EXTERN void  petscdrawlgspdraw_(PetscDrawLG lg,PetscDrawSP spin, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
CHKFORTRANNULLOBJECT(spin);
*ierr = PetscDrawLGSPDraw(
	(PetscDrawLG)PetscToPointer((lg) ),
	(PetscDrawSP)PetscToPointer((spin) ));
}
PETSC_EXTERN void  petscdrawlgcreate_(PetscDraw draw,PetscInt *dim,PetscDrawLG *outlg, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
PetscBool outlg_null = !*(void**) outlg ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(outlg);
*ierr = PetscDrawLGCreate(
	(PetscDraw)PetscToPointer((draw) ),*dim,outlg);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! outlg_null && !*(void**) outlg) * (void **) outlg = (void *)-2;
}
PETSC_EXTERN void  petscdrawlgsetcolors_(PetscDrawLG lg, int colors[], int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
*ierr = PetscDrawLGSetColors(
	(PetscDrawLG)PetscToPointer((lg) ),colors);
}
PETSC_EXTERN void  petscdrawlggetdimension_(PetscDrawLG lg,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
CHKFORTRANNULLINTEGER(dim);
*ierr = PetscDrawLGGetDimension(
	(PetscDrawLG)PetscToPointer((lg) ),dim);
}
PETSC_EXTERN void  petscdrawlgsetdimension_(PetscDrawLG lg,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
*ierr = PetscDrawLGSetDimension(
	(PetscDrawLG)PetscToPointer((lg) ),*dim);
}
PETSC_EXTERN void  petscdrawlgsetlimits_(PetscDrawLG lg,PetscReal *x_min,PetscReal *x_max,PetscReal *y_min,PetscReal *y_max, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
*ierr = PetscDrawLGSetLimits(
	(PetscDrawLG)PetscToPointer((lg) ),*x_min,*x_max,*y_min,*y_max);
}
PETSC_EXTERN void  petscdrawlgreset_(PetscDrawLG lg, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
*ierr = PetscDrawLGReset(
	(PetscDrawLG)PetscToPointer((lg) ));
}
PETSC_EXTERN void  petscdrawlgdestroy_(PetscDrawLG *lg, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(lg);
 PetscBool lg_null = !*(void**) lg ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lg);
*ierr = PetscDrawLGDestroy(lg);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lg_null && !*(void**) lg) * (void **) lg = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(lg);
 }
PETSC_EXTERN void  petscdrawlgsetusemarkers_(PetscDrawLG lg,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
*ierr = PetscDrawLGSetUseMarkers(
	(PetscDrawLG)PetscToPointer((lg) ),*flg);
}
PETSC_EXTERN void  petscdrawlgdraw_(PetscDrawLG lg, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
*ierr = PetscDrawLGDraw(
	(PetscDrawLG)PetscToPointer((lg) ));
}
PETSC_EXTERN void  petscdrawlgsave_(PetscDrawLG lg, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
*ierr = PetscDrawLGSave(
	(PetscDrawLG)PetscToPointer((lg) ));
}
PETSC_EXTERN void  petscdrawlgview_(PetscDrawLG lg,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscDrawLGView(
	(PetscDrawLG)PetscToPointer((lg) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscdrawlgsetoptionsprefix_(PetscDrawLG lg, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(lg);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscDrawLGSetOptionsPrefix(
	(PetscDrawLG)PetscToPointer((lg) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  petscdrawlgsetfromoptions_(PetscDrawLG lg, int *ierr)
{
CHKFORTRANNULLOBJECT(lg);
*ierr = PetscDrawLGSetFromOptions(
	(PetscDrawLG)PetscToPointer((lg) ));
}
#if defined(__cplusplus)
}
#endif
