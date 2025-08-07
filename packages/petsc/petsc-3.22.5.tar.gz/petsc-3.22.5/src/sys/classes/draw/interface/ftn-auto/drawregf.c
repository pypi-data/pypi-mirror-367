#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* drawreg.c */
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
#include "petscviewer.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawview_ PETSCDRAWVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawview_ petscdrawview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawviewfromoptions_ PETSCDRAWVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawviewfromoptions_ petscdrawviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawcreate_ PETSCDRAWCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawcreate_ petscdrawcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsettype_ PETSCDRAWSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsettype_ petscdrawsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawgettype_ PETSCDRAWGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawgettype_ petscdrawgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsetoptionsprefix_ PETSCDRAWSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsetoptionsprefix_ petscdrawsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsetfromoptions_ PETSCDRAWSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsetfromoptions_ petscdrawsetfromoptions
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawview_(PetscDraw indraw,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(indraw);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscDrawView(
	(PetscDraw)PetscToPointer((indraw) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscdrawviewfromoptions_(PetscDraw A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscDrawViewFromOptions(
	(PetscDraw)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscdrawcreate_(MPI_Fint * comm, char display[], char title[],int *x,int *y,int *w,int *h,PetscDraw *indraw, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
PetscBool indraw_null = !*(void**) indraw ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(indraw);
/* insert Fortran-to-C conversion for display */
  FIXCHAR(display,cl0,_cltmp0);
/* insert Fortran-to-C conversion for title */
  FIXCHAR(title,cl1,_cltmp1);
*ierr = PetscDrawCreate(
	MPI_Comm_f2c(*(comm)),_cltmp0,_cltmp1,*x,*y,*w,*h,indraw);
  FREECHAR(display,_cltmp0);
  FREECHAR(title,_cltmp1);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! indraw_null && !*(void**) indraw) * (void **) indraw = (void *)-2;
}
PETSC_EXTERN void  petscdrawsettype_(PetscDraw draw,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = PetscDrawSetType(
	(PetscDraw)PetscToPointer((draw) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  petscdrawgettype_(PetscDraw draw,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawGetType(
	(PetscDraw)PetscToPointer((draw) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  petscdrawsetoptionsprefix_(PetscDraw draw, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscDrawSetOptionsPrefix(
	(PetscDraw)PetscToPointer((draw) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  petscdrawsetfromoptions_(PetscDraw draw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawSetFromOptions(
	(PetscDraw)PetscToPointer((draw) ));
}
#if defined(__cplusplus)
}
#endif
