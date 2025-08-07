#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* matcoloring.c */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringcreate_ MATCOLORINGCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringcreate_ matcoloringcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringdestroy_ MATCOLORINGDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringdestroy_ matcoloringdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringsettype_ MATCOLORINGSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringsettype_ matcoloringsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringsetfromoptions_ MATCOLORINGSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringsetfromoptions_ matcoloringsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringsetdistance_ MATCOLORINGSETDISTANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringsetdistance_ matcoloringsetdistance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringgetdistance_ MATCOLORINGGETDISTANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringgetdistance_ matcoloringgetdistance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringsetmaxcolors_ MATCOLORINGSETMAXCOLORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringsetmaxcolors_ matcoloringsetmaxcolors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringgetmaxcolors_ MATCOLORINGGETMAXCOLORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringgetmaxcolors_ matcoloringgetmaxcolors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringapply_ MATCOLORINGAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringapply_ matcoloringapply
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringview_ MATCOLORINGVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringview_ matcoloringview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringsetweighttype_ MATCOLORINGSETWEIGHTTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringsetweighttype_ matcoloringsetweighttype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcoloringcreate_(Mat m,MatColoring *mcptr, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(mcptr);
 CHKFORTRANNULLOBJECT(m);
PetscBool mcptr_null = !*(void**) mcptr ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mcptr);
*ierr = MatColoringCreate(
	(Mat)PetscToPointer((m) ),mcptr);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mcptr_null && !*(void**) mcptr) * (void **) mcptr = (void *)-2;
}
PETSC_EXTERN void  matcoloringdestroy_(MatColoring *mc, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(mc);
 PetscBool mc_null = !*(void**) mc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mc);
*ierr = MatColoringDestroy(mc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mc_null && !*(void**) mc) * (void **) mc = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(mc);
 }
PETSC_EXTERN void  matcoloringsettype_(MatColoring mc,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mc);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = MatColoringSetType(
	(MatColoring)PetscToPointer((mc) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  matcoloringsetfromoptions_(MatColoring mc, int *ierr)
{
CHKFORTRANNULLOBJECT(mc);
*ierr = MatColoringSetFromOptions(
	(MatColoring)PetscToPointer((mc) ));
}
PETSC_EXTERN void  matcoloringsetdistance_(MatColoring mc,PetscInt *dist, int *ierr)
{
CHKFORTRANNULLOBJECT(mc);
*ierr = MatColoringSetDistance(
	(MatColoring)PetscToPointer((mc) ),*dist);
}
PETSC_EXTERN void  matcoloringgetdistance_(MatColoring mc,PetscInt *dist, int *ierr)
{
CHKFORTRANNULLOBJECT(mc);
CHKFORTRANNULLINTEGER(dist);
*ierr = MatColoringGetDistance(
	(MatColoring)PetscToPointer((mc) ),dist);
}
PETSC_EXTERN void  matcoloringsetmaxcolors_(MatColoring mc,PetscInt *maxcolors, int *ierr)
{
CHKFORTRANNULLOBJECT(mc);
*ierr = MatColoringSetMaxColors(
	(MatColoring)PetscToPointer((mc) ),*maxcolors);
}
PETSC_EXTERN void  matcoloringgetmaxcolors_(MatColoring mc,PetscInt *maxcolors, int *ierr)
{
CHKFORTRANNULLOBJECT(mc);
CHKFORTRANNULLINTEGER(maxcolors);
*ierr = MatColoringGetMaxColors(
	(MatColoring)PetscToPointer((mc) ),maxcolors);
}
PETSC_EXTERN void  matcoloringapply_(MatColoring mc,ISColoring *coloring, int *ierr)
{
CHKFORTRANNULLOBJECT(mc);
PetscBool coloring_null = !*(void**) coloring ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(coloring);
*ierr = MatColoringApply(
	(MatColoring)PetscToPointer((mc) ),coloring);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! coloring_null && !*(void**) coloring) * (void **) coloring = (void *)-2;
}
PETSC_EXTERN void  matcoloringview_(MatColoring mc,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(mc);
CHKFORTRANNULLOBJECT(viewer);
*ierr = MatColoringView(
	(MatColoring)PetscToPointer((mc) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  matcoloringsetweighttype_(MatColoring mc,MatColoringWeightType *wt, int *ierr)
{
CHKFORTRANNULLOBJECT(mc);
*ierr = MatColoringSetWeightType(
	(MatColoring)PetscToPointer((mc) ),*wt);
}
#if defined(__cplusplus)
}
#endif
